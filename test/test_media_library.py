import unittest
import os
import plexcleaner.database as database
from plexcleaner.media import Library, Movie

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class TestMediaLibrary(unittest.TestCase):
    _nb_movie = 98
    _effective_size = 100275991932

    def test_init(self):
        with database.Database(database_override='./test/database/com.plexapp.plugins.library.db') as db:
            library = Library(db)
            self.assertEqual(len(library), self._nb_movie)

    def test_update_library(self):
        with database.Database(database_override='./test/database/com.plexapp.plugins.library.db') as db:
            library = Library(db)
            movie = Movie(1, u"a", "b", 1, 2, 2.2, "d", "e")
            library._update_library(movie)
            self.assertEqual(len(library), self._nb_movie + 1)

    def test_effective_size(self):
        with database.Database(database_override='./test/database/com.plexapp.plugins.library.db') as db:
            library = Library(db)
            movie = Movie(2, u"a", 'b', 1, 2, 2.2, 'd', 'e')
            movie.exist = False
            library._update_library(movie)
            self.assertEqual(library.effective_size, self._effective_size)
            movie.exist = True
            movie.matched = True
            library._update_library(movie)
            self.assertEqual(library.effective_size, self._effective_size + 2)

    def test_iter(self):
        with database.Database(database_override='./test/database/com.plexapp.plugins.library.db') as db:
            library = Library(db)
            self.assertEqual(type(library.__iter__()).__name__, 'generator')
            m = library.__iter__().next()
            self.assertEqual(m.__class__.__name__, 'Movie')

    def test_has_missing_file(self):
        with database.Database(database_override='./test/database/com.plexapp.plugins.library.db') as db:
            library = Library(db)
            self.assertFalse(library.has_missing_file)
            os.rename('test/library/2 Guns.avi', 'test/library/Two Guns.avi')

        with database.Database(database_override='./test/database/com.plexapp.plugins.library.db') as db:
            library = Library(db)
            self.assertTrue(library.has_missing_file)
            os.rename('test/library/Two Guns.avi', 'test/library/2 Guns.avi')
