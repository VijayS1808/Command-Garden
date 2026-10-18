"""Local SQLite storage. No network access or command execution."""
import json
import os
import sqlite3
import uuid
import zipfile
from pathlib import Path
from datetime import datetime, timezone

KINDS = ['Command', 'Script', 'Note', 'Link', 'Image']
COLORS = ['Lavender', 'Mint', 'Peach', 'Sky', 'Rose']

def now():
    return datetime.now(timezone.utc).isoformat()

class Store:
    def __init__(self, root=None):
        self.root = Path(root or Path(os.environ.get('XDG_DATA_HOME', Path.home()/'.local/share'))/'command-garden')
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(self.root/'garden.sqlite3')
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('''CREATE TABLE IF NOT EXISTS entries (
          id TEXT PRIMARY KEY, title TEXT, kind TEXT, category TEXT, tags TEXT,
          emoji TEXT, color TEXT, body TEXT, favorite INTEGER, updated TEXT)''')
        self.db.execute('''CREATE TABLE IF NOT EXISTS images (
          id TEXT PRIMARY KEY, entry_id TEXT, name TEXT, data BLOB)''')
        self.db.commit()

    def all(self):
        return [dict(r) for r in self.db.execute('SELECT * FROM entries ORDER BY updated DESC')]

    def put(self, entry):
        entry = dict(entry)
        entry['updated'] = now()
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO entries VALUES (:id,:title,:kind,:category,:tags,:emoji,:color,:body,:favorite,:updated)', entry)
        return entry

    def new(self, kind='Note'):
        return self.put(dict(id=uuid.uuid4().hex, title='Untitled '+kind.lower(), kind=kind,
          category='Personal', tags='', emoji={'Command':'⚡','Script':'🐍','Note':'📝','Link':'🔗','Image':'🖼'}.get(kind,'📝'),
          color='Lavender', body='', favorite=0, updated=now()))

    def delete(self, entry_id):
        with self.db:
            self.db.execute('DELETE FROM images WHERE entry_id=?', (entry_id,))
            self.db.execute('DELETE FROM entries WHERE id=?', (entry_id,))

    def images(self, entry_id):
        return [dict(r) for r in self.db.execute('SELECT * FROM images WHERE entry_id=?', (entry_id,))]

    def add_image(self, entry_id, name, data):
        with self.db:
            self.db.execute('INSERT INTO images VALUES (?,?,?,?)', (uuid.uuid4().hex, entry_id, name, data))

    def export(self, path):
        path = Path(path)
        tmp = path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
        try:
            with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
                manifest = dict(format='command-garden', version=1, entries=self.all(), images=[])
                for r in self.db.execute('SELECT * FROM images'):
                    item = dict(r); data = item.pop('data')
                    manifest['images'].append(item)
                    z.writestr('images/'+item['id'], data)
                z.writestr('garden.json', json.dumps(manifest, ensure_ascii=False))
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)

    def restore(self, path):
        # Validate completely before a single transaction. Import creates new IDs.
        with zipfile.ZipFile(path) as z:
            if sum(i.file_size for i in z.infolist()) > 256*1024*1024:
                raise ValueError('Backup is larger than the 256 MB import limit.')
            doc = json.loads(z.read('garden.json'))
            if doc.get('format') != 'command-garden' or doc.get('version') != 1:
                raise ValueError('This is not a supported Command Garden backup.')
            rows = doc['entries']; images = doc['images']; mapping = {}
            columns = ['id','title','kind','category','tags','emoji','color','body','favorite','updated']
            for row in rows:
                if any(not isinstance(row.get(k), str) for k in columns if k != 'favorite') or row.get('favorite') not in (0,1):
                    raise ValueError('Invalid entry in backup.')
                if row['kind'] not in KINDS or row['color'] not in COLORS or row['id'] in mapping:
                    raise ValueError('Invalid entry type, colour, or duplicate ID.')
                mapping[row['id']] = uuid.uuid4().hex
            blobs = []
            for img in images:
                if img['entry_id'] not in mapping or not isinstance(img['name'], str):
                    raise ValueError('Invalid attachment.')
                blobs.append((uuid.uuid4().hex, mapping[img['entry_id']], img['name'], z.read('images/'+img['id'])))
            with self.db:
                for row in rows:
                    vals = [mapping[row['id']]]+[row[k] for k in columns[1:]]
                    self.db.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?)', vals)
                self.db.executemany('INSERT INTO images VALUES (?,?,?,?)', blobs)
        return len(rows)
