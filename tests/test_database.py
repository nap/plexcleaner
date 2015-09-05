import unittest
from plexcleaner.exception import PlexCleanerException
from plexcleaner.database import Database

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'
# flake8: noqa


class TestDatabase(unittest.TestCase):
    def get_db(self):
        db = Database(database_override=':memory:')
        db._cursor.execute('CREATE TABLE media_parts(id, file)')
        db._cursor.executemany('INSERT INTO media_parts(id, file) VALUES (?, ?)', [(1, '/tests/fail'),
                                                                                   (2, '/tests/fail'),
                                                                                   (3, '/tests/fail')])
        db.commit()
        return db

    def test_database_exception(self):
        with self.assertRaises(PlexCleanerException) as e:
            db = Database(database_override='./path/to/com.plexapp.plugins.library.db')
            self.assertFalse(db.has_uncommited())
        self.assertTrue('Could not connect' in e.exception.message)

    def test_update(self):
        db = self.get_db()
        db.update_row(1, '/tests/success')
        row = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (1,)).fetchone()
        self.assertEqual(row[0], '/tests/success')

    def test_update_many(self):
        db = self.get_db()
        db.update_many_row([('/tests/success', 1), ('/tests/success', 2), ('/tests/success', 3)])
        for row in db._cursor.execute('SELECT file FROM media_parts').fetchall():
            self.assertEqual(row[0], '/tests/success')

    def test_get_rows(self):
        db = Database(database_override='./tests/database/com.plexapp.plugins.library.db')
        rows = db.get_rows().fetchall()
        self.assertEqual(len(rows), 98)

    def test_with_enter_exit(self):
        with Database(database_override='./tests/database/com.plexapp.plugins.library.db') as db:
            rows = db.get_rows().fetchall()
            self.assertEqual(len(rows), 98)

    def test_with_enter_exit_commit(self):
        with Database(database_override='./tests/database/com.plexapp.plugins.library.db') as db:
            db._uncommited = True
            db._cursor.execute('UPDATE media_parts SET hash = ? WHERE id = ?', ('tests', 1))

        with Database(database_override='./tests/database/com.plexapp.plugins.library.db') as db:
            result = db._cursor.execute('SELECT hash FROM media_parts WHERE id = ?', (1, )).fetchone()
            self.assertEqual('tests', result[0])

    def test_rollback(self):
        db = self.get_db()
        db.update_row(1, '/tests/success')
        row = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (1,)).fetchone()
        self.assertEqual(row[0], '/tests/success')
        db.rollback()
        row = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (1,)).fetchone()
        self.assertEqual(row[0], '/tests/fail')

    def test_has_uncommited_single(self):
        db = self.get_db()
        db.update_row(1, '/tests/success')
        self.assertTrue(db.has_uncommited())
        db.commit()
        self.assertFalse(db.has_uncommited())

    def test_has_uncommited_multiple(self):
        db = self.get_db()
        db.update_many_row([('/tests/success', 1), ('/tests/success', 2), ('/tests/success', 3)])
        self.assertTrue(db.has_uncommited())
        db.commit()
        self.assertFalse(db.has_uncommited())

    def test_database_exception_init(self):
        with self.assertRaises(PlexCleanerException) as e:
            db = Database(database_override='./tests/database/bad.db')
            db.get_rows()
        self.assertTrue('Could not open' in e.exception.message)

    def test_database_exception_rows(self):
        with self.assertRaises(PlexCleanerException) as e:
            db = Database(database_override='./tests/database/empty.db')
            db.get_rows()
        self.assertTrue('Unabled to fetch' in e.exception.message)
