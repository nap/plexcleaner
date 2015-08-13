import unittest
import os
from plexcleaner.media import Library, Movie
from plexcleaner.exception import PlexCleanerException

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class TestMediaLibrary(unittest.TestCase):
    _nb_movie = 98
    _effective_size = 100275991932

    def test_init(self):
        library = Library(database_override='test/database/com.plexapp.plugins.library.db')
        self.assertEqual(len(library), self._nb_movie)

    def test_update_library(self):
        library = Library(database_override='test/database/com.plexapp.plugins.library.db')
        movie = Movie(1, u"a", "b", 1, 2, 2.2, "d", "e")
        library._update_library(movie)
        self.assertEqual(len(library), self._nb_movie + 1)

    def test_database_exception(self):
        with self.assertRaises(PlexCleanerException) as e:
            library = Library(database_override='database/some.bad.name.db')
        self.assertTrue('Could not connect' in e.exception.message)

    def test_effective_size(self):
        library = Library(database_override='test/database/com.plexapp.plugins.library.db')
        movie = Movie(2, u"a", 'b', 1, 2, 2.2, 'd', 'e')
        movie.exist = False
        library._update_library(movie)
        self.assertEqual(library.effective_size, self._effective_size)
        movie.exist = True
        movie.matched = True
        library._update_library(movie)
        self.assertEqual(library.effective_size, self._effective_size + 2)

    def test_iter(self):
        library = Library(database_override='test/database/com.plexapp.plugins.library.db')
        self.assertEqual(type(library.__iter__()).__name__, 'generator')
        m = library.__iter__().next()
        self.assertEqual(m.__class__.__name__, 'Movie')

    def test_has_missing_file(self):
        library = Library(database_override='test/database/com.plexapp.plugins.library.db')
        self.assertFalse(library.has_missing_file)
        os.rename('test/library/2 Guns.avi', 'test/library/Two Guns.avi')
        library = Library(database_override='test/database/com.plexapp.plugins.library.db')
        self.assertTrue(library.has_missing_file)
        os.rename('test/library/Two Guns.avi', 'test/library/2 Guns.avi')

if __name__ == '__main__':
    unittest.main()
