#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path
from PyQt5.QtCore import Qt, QTimer, QUrl, QLockFile
from PyQt5.QtGui import QColor, QFont, QPixmap, QDesktopServices, QSyntaxHighlighter, QTextCharFormat, QKeySequence, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QListWidget, QListWidgetItem, QTextEdit,
    QPlainTextEdit, QSplitter, QTabWidget, QFileDialog, QMessageBox, QScrollArea,
    QShortcut, QFrame, QInputDialog)
from store import Store, KINDS, COLORS

PALETTE = dict(Lavender='#a998ef', Mint='#72cfb5', Peach='#efb18a', Sky='#86bdef', Rose='#e99dba')

class Highlight(QSyntaxHighlighter):
    def highlightBlock(self, text):
        rules = [(r'\b(if|else|elif|for|while|do|done|fi|then|def|class|return|import|from|in|try|except|echo|sudo|cat|grep|sort|print|function|const|let)\b','#a998ef'),
                 (r'(--?[\w-]+)','#72cfb5'), (r'\b\d+\b','#efb18a'),
                 (r'"[^"\n]*"|\x27[^\x27\n]*\x27','#e7c789'), (r'#.*$','#71809c')]
        for pattern, color in rules:
            fmt = QTextCharFormat(); fmt.setForeground(QColor(color))
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end()-match.start(), fmt)

class Window(QMainWindow):
    def __init__(self, store):
        super().__init__(); self.store=store; self.current=None; self.loading=False; self.dirty=False; self.filter='All items'
        self.setWindowTitle('Command Garden • Your local workspace'); self.resize(1280,830)
        self.setWindowIcon(QIcon(str(Path(__file__).with_name('icon.svg'))))
        self.timer=QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.save)
        root=QWidget(); self.setCentralWidget(root); outer=QHBoxLayout(root); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        sidebar=QWidget(); sidebar.setObjectName('sidebar'); sidebar.setFixedWidth(215); side=QVBoxLayout(sidebar); side.setContentsMargins(20,26,20,24); side.setSpacing(12)
        logo=QLabel('🌱  Command\n      Garden'); logo.setObjectName('logo'); side.addWidget(logo)
        tagline=QLabel('A home for your ideas.'); tagline.setObjectName('muted'); side.addWidget(tagline); side.addSpacing(24)
        self.nav=QListWidget(); self.nav.setObjectName('nav')
        for icon,name in [('◈','All items'),('★','Favourites'),('⚡','Command'),('🐍','Script'),('📝','Note'),('🔗','Link'),('🖼','Image')]:
            item=QListWidgetItem(icon+'   '+name); item.setData(Qt.UserRole,name); self.nav.addItem(item)
        self.nav.setCurrentRow(0); self.nav.currentItemChanged.connect(self.filter_changed); side.addWidget(self.nav)
        self.button(side,'↗  Export backup',self.export_backup)
        self.button(side,'↙  Import backup',self.import_backup)
        local_note=QLabel('●  Local & offline\nSaved on this PC.'); local_note.setWordWrap(True); side.addWidget(local_note); outer.addWidget(sidebar)
        main=QWidget(); layout=QVBoxLayout(main); layout.setContentsMargins(28,24,28,18); layout.setSpacing(18); outer.addWidget(main)
        top=QHBoxLayout(); title=QVBoxLayout(); h=QLabel('Your personal command library'); h.setObjectName('heading'); title.addWidget(h)
        sub=QLabel('Keep useful things. Find them when you need them.'); sub.setObjectName('muted'); title.addWidget(sub); top.addLayout(title); top.addStretch()
        self.button(top,'＋ New item',self.new_item,'primary'); layout.addLayout(top)
        tools=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText('⌕  Search titles, commands, tags…  (Ctrl+F)'); self.search.textChanged.connect(self.refresh); tools.addWidget(self.search,1)
        self.category_filter=QComboBox(); self.category_filter.setMinimumWidth(150); self.category_filter.addItem('All categories'); self.category_filter.currentTextChanged.connect(self.refresh); tools.addWidget(self.category_filter)
        self.sort=QComboBox(); self.sort.addItems(['Recently edited','Title A → Z']); self.sort.currentIndexChanged.connect(self.refresh); tools.addWidget(self.sort); layout.addLayout(tools)
        split=QSplitter(); layout.addWidget(split,1)
        left=QWidget(); ll=QVBoxLayout(left); ll.setContentsMargins(0,0,12,0); self.count=QLabel(); self.count.setObjectName('muted'); ll.addWidget(self.count)
        self.items=QListWidget(); self.items.setObjectName('cards'); self.items.setSpacing(6); self.items.setWordWrap(True); self.items.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.items.currentItemChanged.connect(self.select); ll.addWidget(self.items); split.addWidget(left)
        self.panel=QWidget(); self.panel.setObjectName('editorPanel'); ed=QVBoxLayout(self.panel); ed.setContentsMargins(22,20,22,20); ed.setSpacing(14); split.addWidget(self.panel); split.setSizes([330,650])
        row=QHBoxLayout(); self.emoji=QComboBox(); self.emoji.setEditable(True); self.emoji.addItems(['⚡','🐍','📝','🔗','🖼','🔍','🛠','💡','🚀','🐧','🎯','📌','💻','🌿']); self.emoji.setFixedWidth(82); row.addWidget(self.emoji)
        self.title=QLineEdit(); self.title.setObjectName('entryTitle'); self.title.setPlaceholderText('Give this a title…'); row.addWidget(self.title,1)
        self.star=QPushButton('☆'); self.star.setCheckable(True); self.star.setFixedWidth(45); self.star.toggled.connect(lambda checked:self.star.setText('★' if checked else '☆')); row.addWidget(self.star); ed.addLayout(row)
        row=QHBoxLayout(); self.kind=QComboBox(); self.kind.addItems(KINDS); row.addWidget(self.kind)
        self.category=QLineEdit(); self.category.setPlaceholderText('Category, e.g. Linux'); row.addWidget(self.category,1)
        self.color=QComboBox(); self.color.addItems(COLORS); row.addWidget(self.color); ed.addLayout(row)
        self.tags=QLineEdit(); self.tags.setPlaceholderText('Tags  •  linux, recon, useful'); ed.addWidget(self.tags)
        bar=QHBoxLayout()
        for text,fn in [('B',lambda:self.wrap('**')),('I',lambda:self.wrap('*')),('Code',lambda:self.wrap('`')),('☑ List',lambda:self.insert('- [ ] ')),('Link',self.insert_link)]: self.button(bar,text,fn)
        bar.addStretch(); self.button(bar,'Copy',self.copy); self.button(bar,'Open link ↗',self.open_link); ed.addLayout(bar)
        self.tabs=QTabWidget(); self.tabs.setMinimumHeight(260); self.editor=QPlainTextEdit(); self.editor.setPlaceholderText('Paste a command, write a script, or capture an idea…\n\nNotes support Markdown. Use Preview to read formatted notes.'); self.editor.setFont(QFont('DejaVu Sans Mono',11)); self.editor.setTabStopDistance(32)
        self.highlighter=Highlight(self.editor.document()); self.preview=QTextEdit(); self.preview.setReadOnly(True); self.preview.setAcceptRichText(False)
        self.tabs.addTab(self.editor,'✎  Editor'); self.tabs.addTab(self.preview,'◉  Preview'); self.tabs.currentChanged.connect(self.update_preview); ed.addWidget(self.tabs,1)
        attachbar=QHBoxLayout(); attachbar.addWidget(QLabel('ATTACHMENTS')); attachbar.addStretch(); self.button(attachbar,'＋ Add image',self.add_image); self.button(attachbar,'Import text',self.import_text); ed.addLayout(attachbar)
        self.attachments=QListWidget(); self.attachments.setMaximumHeight(85); self.attachments.itemDoubleClicked.connect(self.show_image); ed.addWidget(self.attachments)
        foot=QHBoxLayout(); self.state=QLabel('Saved locally'); self.state.setObjectName('muted'); foot.addWidget(self.state,1); self.button(foot,'Save',self.save); self.button(foot,'Delete',self.delete); ed.addLayout(foot)
        for field in [self.title,self.category,self.tags]: field.textChanged.connect(self.changed)
        for field in [self.emoji,self.kind,self.color]: field.currentTextChanged.connect(self.changed)
        self.editor.textChanged.connect(self.changed); self.star.toggled.connect(self.changed)
        for key,fn in [('Ctrl+S',self.save),('Ctrl+N',self.new_item),('Ctrl+F',self.search.setFocus)]: QShortcut(QKeySequence(key),self,activated=fn)
        self.setStyleSheet(STYLE)
        self.refresh(); self.panel.setEnabled(False)
        if self.items.count(): self.items.setCurrentRow(0)
        self.statusBar().showMessage('Tip: Ctrl+N new item  •  Ctrl+S save  •  Double-click an attachment to view it')

    def button(self, layout, text, fn, name=''):
        b=QPushButton(text); b.setCursor(Qt.PointingHandCursor); b.setObjectName(name); b.clicked.connect(lambda _=False:fn()); layout.addWidget(b); return b

    def error(self, exc): QMessageBox.critical(self,'Could not complete action',str(exc))

    def filter_changed(self, item, old):
        if item: self.filter=item.data(Qt.UserRole); self.refresh()

    def refresh(self, *_):
        selected=self.current['id'] if self.current else None
        rows=self.store.all(); cat=self.category_filter.currentText()
        self.category_filter.blockSignals(True); self.category_filter.clear(); self.category_filter.addItems(['All categories']+sorted(set(r['category'] for r in rows if r['category'])))
        self.category_filter.setCurrentText(cat if self.category_filter.findText(cat)>=0 else 'All categories'); self.category_filter.blockSignals(False)
        q=self.search.text().casefold(); cat=self.category_filter.currentText()
        rows=[r for r in rows if (self.filter=='All items' or self.filter=='Favourites' and r['favorite'] or self.filter==r['kind']) and (cat=='All categories' or cat==r['category']) and q in ' '.join(str(r[k]) for k in ['title','body','tags','category']).casefold()]
        if self.sort.currentIndex(): rows.sort(key=lambda r:r['title'].casefold())
        self.items.blockSignals(True); self.items.clear()
        for r in rows:
            snippet=' '.join(r['body'].split())[:66] or 'Start writing something useful…'
            item=QListWidgetItem(f"{r['emoji']}  {r['title'][:40]} {'★' if r['favorite'] else ''}\n\n{r['kind'].upper()}  ·  {r['category']}\n{snippet}")
            item.setData(Qt.UserRole,r); item.setForeground(QColor(PALETTE[r['color']])); self.items.addItem(item)
            if r['id']==selected: self.items.setCurrentItem(item)
        self.items.blockSignals(False); self.count.setText(f'{len(rows)} ITEMS  /  {len(self.store.all())} IN YOUR GARDEN')

    def select(self,item,old):
        if not item:return
        selected=dict(item.data(Qt.UserRole))
        if not self.save():
            self.refresh(); return
        self.current=selected; self.loading=True; r=self.current
        self.panel.setEnabled(True)
        for field,key in [(self.title,'title'),(self.category,'category'),(self.tags,'tags')]:field.setText(r[key])
        for field,key in [(self.emoji,'emoji'),(self.kind,'kind'),(self.color,'color')]:field.setCurrentText(r[key])
        self.star.setChecked(bool(r['favorite'])); self.editor.setPlainText(r['body']); self.loading=False; self.dirty=False
        self.state.setText('✓ Saved locally'); self.load_images(); self.update_preview()

    def changed(self,*_):
        if self.loading or not self.current:return
        self.dirty=True; self.state.setText('Saving…'); self.timer.start(650)

    def save(self):
        self.timer.stop()
        if not self.current or not self.dirty:return True
        try:
            r=dict(self.current); r.update(title=self.title.text(),category=self.category.text(),tags=self.tags.text(),emoji=self.emoji.currentText(),kind=self.kind.currentText(),color=self.color.currentText(),body=self.editor.toPlainText(),favorite=int(self.star.isChecked()))
            self.current=self.store.put(r); self.dirty=False; self.state.setText('✓ Saved locally'); self.refresh(); self.update_preview(); return True
        except Exception as e:self.state.setText('Save failed — content is still in editor'); self.error(e); return False

    def new_item(self):
        if not self.save():return
        kind,ok=QInputDialog.getItem(self,'New item','What would you like to save?',KINDS,0,False)
        if not ok:return
        try:
            r=self.store.new(kind); self.search.clear(); self.category_filter.setCurrentIndex(0); self.nav.setCurrentRow(0); self.refresh()
            for i in range(self.items.count()):
                if self.items.item(i).data(Qt.UserRole)['id']==r['id']:self.items.setCurrentRow(i);break
            self.title.setFocus(); self.title.selectAll()
        except Exception as e:self.error(e)

    def update_preview(self,*_):
        if not self.current:return
        if self.kind.currentText() in ['Command','Script']:self.preview.setPlainText(self.editor.toPlainText())
        else:self.preview.setMarkdown(self.editor.toPlainText())

    def wrap(self,mark):
        c=self.editor.textCursor(); c.insertText(mark+c.selectedText().replace('\u2029','\n')+mark); self.editor.setTextCursor(c); self.editor.setFocus()
    def insert(self,text):self.editor.insertPlainText(text); self.editor.setFocus()
    def insert_link(self):self.insert('[Link title](https://example.com)')
    def copy(self):QApplication.clipboard().setText(self.editor.toPlainText()); self.statusBar().showMessage('Copied to clipboard',3000)
    def open_link(self):
        matches=re.findall(r'https?://[^\s<>\)\]"\x27]+',self.editor.toPlainText())
        if not matches:QMessageBox.information(self,'Open link','Add an https:// or http:// link to this entry.');return
        link,ok=QInputDialog.getItem(self,'Open in browser','Choose a link:',list(dict.fromkeys(matches)),0,False)
        if ok:QDesktopServices.openUrl(QUrl(link))

    def add_image(self):
        paths,_=QFileDialog.getOpenFileNames(self,'Attach images','','Images (*.png *.jpg *.jpeg *.webp *.gif *.bmp)')
        try:
            for path in paths:
                p=Path(path)
                if p.stat().st_size>20*1024*1024:raise ValueError('Please choose images smaller than 20 MB.')
                data=p.read_bytes(); pix=QPixmap()
                if not pix.loadFromData(data):raise ValueError('Unsupported or damaged image: '+p.name)
                self.store.add_image(self.current['id'],p.name,data)
            self.load_images()
        except Exception as e:self.error(e)

    def load_images(self):
        self.attachments.clear()
        for img in self.store.images(self.current['id']):
            item=QListWidgetItem('🖼  '+img['name']+'   ·   double-click to view'); item.setData(Qt.UserRole,img); self.attachments.addItem(item)

    def show_image(self,item):
        img=item.data(Qt.UserRole); win=QMainWindow(self); win.setWindowTitle(img['name']); win.resize(800,650)
        area=QScrollArea(); label=QLabel(); pix=QPixmap(); pix.loadFromData(img['data']); label.setPixmap(pix.scaled(1000,800,Qt.KeepAspectRatio,Qt.SmoothTransformation)); area.setWidget(label); win.setCentralWidget(area)
        bar=win.addToolBar('Image'); save=bar.addAction('Save image as…'); remove=bar.addAction('Remove attachment')
        def export_image():
            path,_=QFileDialog.getSaveFileName(win,'Save image',img['name'])
            if path:
                try:Path(path).write_bytes(img['data'])
                except Exception as e:self.error(e)
        def remove_image():
            if QMessageBox.question(win,'Remove attachment','Remove this image from this entry?')==QMessageBox.Yes:
                try:
                    with self.store.db:self.store.db.execute('DELETE FROM images WHERE id=?',(img['id'],))
                    self.load_images();win.close()
                except Exception as e:self.error(e)
        save.triggered.connect(export_image); remove.triggered.connect(remove_image); win.show()

    def import_text(self):
        path,_=QFileDialog.getOpenFileName(self,'Import a text file or script')
        if not path:return
        try:
            if Path(path).stat().st_size>2*1024*1024:raise ValueError('Text import limit is 2 MB.')
            text=Path(path).read_text(encoding='utf-8')
            if self.editor.toPlainText() and QMessageBox.question(self,'Replace editor text?','Replace this entry’s text with the selected file?')!=QMessageBox.Yes:return
            self.editor.setPlainText(text)
        except Exception as e:self.error(e)

    def delete(self):
        if not self.current:return
        if QMessageBox.question(self,'Delete item?','Delete this item and its attachments? This cannot be undone.')!=QMessageBox.Yes:return
        try:
            self.store.delete(self.current['id']); self.timer.stop(); self.current=None; self.dirty=False; self.refresh(); self.panel.setEnabled(False); self.editor.clear(); self.title.clear(); self.attachments.clear()
            if self.items.count():self.items.setCurrentRow(0)
        except Exception as e:self.error(e)

    def export_backup(self):
        if not self.save():return
        path,_=QFileDialog.getSaveFileName(self,'Export all entries and images','command-garden-backup.zip','ZIP backup (*.zip)')
        if path:
            try:self.store.export(path); QMessageBox.information(self,'Backup saved','All entries and images were exported. Keep a copy on another drive for recovery.')
            except Exception as e:self.error(e)
    def import_backup(self):
        if not self.save():return
        path,_=QFileDialog.getOpenFileName(self,'Import backup','','ZIP backup (*.zip)')
        if not path:return
        if QMessageBox.question(self,'Import backup','Add all backup items as new copies? Existing entries will remain unchanged.')!=QMessageBox.Yes:return
        try:
            n=self.store.restore(path); self.refresh(); QMessageBox.information(self,'Import complete',f'Added {n} items.')
        except Exception as e:self.error(e)
    def closeEvent(self,event):
        if self.save():event.accept()
        else:event.ignore()

STYLE='''
QWidget { background:#141824; color:#e5e9f4; font-family:"DejaVu Sans"; font-size:13px; }
QWidget#sidebar { background:#10131d; border-right:1px solid #2a3042; }
QLabel { background:transparent; }
QLabel#logo { font-size:24px; font-weight:700; color:#c6bafa; }
QLabel#heading { font-size:24px; font-weight:700; }
QLabel#muted { color:#8e9ab2; font-size:12px; }
QPushButton { background:#262d40; border:1px solid #343d55; border-radius:8px; padding:9px 12px; }
QPushButton:hover { background:#38435d; border-color:#a998ef; }
QPushButton#primary { background:#ad9aef; color:#161326; border:0; font-weight:700; padding:12px 18px; }
QPushButton:checked { color:#f1d18b; }
QLineEdit,QComboBox { background:#1c2232; border:1px solid #323b52; border-radius:8px; padding:10px; selection-background-color:#6955a5; }
QLineEdit:focus,QComboBox:focus,QPlainTextEdit:focus { border-color:#a998ef; }
QLineEdit#entryTitle { font-size:20px; font-weight:600; }
QComboBox::drop-down { border:0; width:20px; }
QListWidget { border:0; outline:0; background:transparent; }
QListWidget#nav::item { padding:14px 8px; border-radius:8px; margin-bottom:4px; }
QListWidget#nav::item:selected { background:#2c2744; color:#cfbfff; }
QListWidget#cards::item { background:#1c2232; border:1px solid #30384e; border-radius:12px; padding:18px 14px; }
QListWidget#cards::item:selected { border:1px solid #ae9af1; background:#29273e; }
QListWidget#cards::item:hover { background:#262d40; }
QWidget#editorPanel { background:#191f2d; border:1px solid #30384e; border-radius:14px; }
QPlainTextEdit,QTextEdit { background:#101521; border:1px solid #30384e; padding:14px; selection-background-color:#6955a5; }
QTabWidget::pane { border:0; }
QTabBar::tab { background:#22293b; padding:10px 18px; }
QTabBar::tab:selected { color:#c9b8ff; background:#101521; border-top:2px solid #a998ef; }
QSplitter::handle { background:#141824; width:6px; }
QStatusBar { color:#8e9ab2; background:#10131d; }
QScrollBar:vertical { width:10px; background:#151a27; }
QScrollBar::handle:vertical { background:#424b63; border-radius:4px; min-height:25px; }
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0; }
'''

def main():
    os.umask(0o077)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling,True)
    app=QApplication(sys.argv); app.setApplicationName('Command Garden')
    store=Store(); lock=QLockFile(str(store.root/'app.lock'))
    if not lock.tryLock(100):
        QMessageBox.information(None,'Command Garden','Command Garden is already open.');return
    window=Window(store); window.show(); sys.exit(app.exec_())

if __name__=='__main__':main()
