import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from store import Store
from PyQt5.QtWidgets import QApplication
from app import Window

APP=QApplication.instance() or QApplication([])

class GardenTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.s=Store(self.root/'data')
    def tearDown(self):self.s.db.close(); self.tmp.cleanup()
    def test_persistence_and_backup(self):
        r=self.s.new('Script'); r['body']='echo "🌱"\n# hello'; self.s.put(r)
        self.s.add_image(r['id'],'test.png',b'example-image-bytes')
        self.s.export(self.root/'backup.zip')
        other=Store(self.root/'restored')
        self.assertEqual(other.restore(self.root/'backup.zip'),1)
        row=other.all()[0]; self.assertEqual(row['body'],r['body']); self.assertNotEqual(row['id'],r['id'])
        self.assertEqual(other.images(row['id'])[0]['data'],b'example-image-bytes')
        other.db.close()
        reopened=Store(self.root/'data'); self.assertEqual(reopened.all()[0]['body'],r['body']); reopened.db.close()
    def test_invalid_import_is_atomic(self):
        self.s.new(); count=len(self.s.all())
        with zipfile.ZipFile(self.root/'bad.zip','w') as z:
            z.writestr('garden.json',json.dumps(dict(format='command-garden',version=1,entries=[{'id':'broken'}],images=[])))
        with self.assertRaises(ValueError):self.s.restore(self.root/'bad.zip')
        self.assertEqual(len(self.s.all()),count)
    def test_editor_switch_save_search_and_preview(self):
        one=self.s.new('Command'); two=self.s.new('Note')
        w=Window(self.s); w.show(); APP.processEvents()
        current=w.current['id']; w.editor.setPlainText('**important**\necho hello')
        other=next(w.items.item(i) for i in range(w.items.count()) if w.items.item(i).data(256)['id']!=current)
        target=other.data(256)['id']; w.items.setCurrentItem(other); APP.processEvents()
        self.assertEqual(w.current['id'],target)
        self.assertEqual(next(r for r in self.s.all() if r['id']==current)['body'],'**important**\necho hello')
        w.editor.setPlainText('retained after restart'); self.assertTrue(w.save())
        w.search.setText('important'); self.assertEqual(w.items.count(),1)
        w.search.clear(); w.close()
    def test_delete_removes_attachments(self):
        r=self.s.new(); self.s.add_image(r['id'],'x',b'x'); self.s.delete(r['id'])
        self.assertEqual(self.s.all(),[]); self.assertEqual(self.s.images(r['id']),[])

if __name__=='__main__':unittest.main()
