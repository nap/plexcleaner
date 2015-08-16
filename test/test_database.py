import unittest
from plexcleaner.exception import PlexCleanerException
from plexcleaner.database import Database

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class TestDatabase(unittest.TestCase):

    def test_database_exception(self):
        with self.assertRaises(PlexCleanerException) as e:
            db = Database(database_override='./path/to/com.plexapp.plugins.library.db')
        self.assertTrue('Could not connect' in e.exception.message)
