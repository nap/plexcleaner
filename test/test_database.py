import unittest
from plexcleaner.exception import PlexCleanerException
from plexcleaner.database import Database

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class TestDatabase(unittest.TestCase):
    def get_db(self):
        db = Database(database_override=':memory:')
        db._cursor.execute('CREATE TABLE media_parts(id, file)')
        db._cursor.executemany('INSERT INTO media_parts(id, file) VALUES (?, ?)', [(1, '/test/fail'),
                                                                                   (2, '/test/fail'),
                                                                                   (3, '/test/fail')])
        db.commit()
        return db

    def test_database_exception(self):
        with self.assertRaises(PlexCleanerException) as e:
            db = Database(database_override='./path/to/com.plexapp.plugins.library.db')
        self.assertTrue('Could not connect' in e.exception.message)

    def test_update(self):
        db = self.get_db()
        db.update_row(1, '/test/success')
        row = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (1,)).fetchone()
        self.assertEqual(row[0], '/test/success')

    def test_update_many(self):
        db = self.get_db()
        db.update_many_row([('/test/success', 1), ('/test/success', 2), ('/test/success', 3)])
        for row in db._cursor.execute('SELECT file FROM media_parts').fetchall():
            self.assertEqual(row[0], '/test/success')

    def test_get_rows(self):
        db = Database(database_override='./test/database/com.plexapp.plugins.library.db')
        rows = db.get_rows().fetchall()
        self.assertEqual(len(rows), 98)

    def test_rollback(self):
        db = self.get_db()
        db.update_row(1, '/test/success')
        row = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (1,)).fetchone()
        self.assertEqual(row[0], '/test/success')
        db.rollback()
        row = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (1,)).fetchone()
        self.assertEqual(row[0], '/test/fail')

    def test_has_uncommited(self):
        db = self.get_db()
        db.update_row(1, '/test/success')
        self.assertTrue(db.has_uncommited())
        db.commit()
        self.assertFalse(db.has_uncommited())

if __name__ == '__main__':
    unittest.main()
