import unittest
import os
import hashlib
import json
from plexcleaner.media import Library, Movie
from plexcleaner.exception import PlexDatabaseException

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class TestMediaLibrary(unittest.TestCase):
    _nb_movie = 98
    _effective_size = 100275991932

    def test_init(self):
        library = Library(database_override='test/database/com.plexapp.plugins.library.db')
        self.assertEqual(len(library), self._nb_movie)

    def test_update_library(self):
        library = Library(database_override='test/database/com.plexapp.plugins.library.db')
        movie = Movie(u"a", "b", 1, 2, 2.2, "d", "e")
        library._update_library(movie)
        self.assertEqual(len(library), self._nb_movie + 1)

    def test_database_exception(self):
        with self.assertRaises(PlexDatabaseException) as e:
            library = Library(database_override='database/some.bad.db.name')
        self.assertTrue('Could not connect' in e.exception.message)

    def test_effective_size(self):
        library = Library(database_override='test/database/com.plexapp.plugins.library.db')
        movie = Movie(u"a", 'b', 1, 2, 2.2, 'd', 'e')
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


class TestMediaMovie(unittest.TestCase):
    _lib = os.path.join(os.environ['PYTHONPATH'], 'test/library')
    _jacket = 'metadata://com.plexapp.agents.themoviedb_3eb7a03172ea078adbb484ad9d30bfeda4126e2f'
    _metadata_path = 'Library/Application Support/Plex Media Server/Metadata/Movies'
    _jacket_path = "{0}/{1}.bundle/Contents/_stored/{2}"
    _agent_prefix = 'com.plexapp.agents'

    def test_init(self):
        movie = Movie(u"Burn Notice: The Fall of Sam Axe",
                      os.path.join(self._lib, 'Burn Notice The Fall of Sam Axe.avi'),
                      2010, 2, 2.2, 'someGUID', 'thumb1')
        self.assertFalse(movie.matched)

        movie = Movie(u"Burn Notice: The Fall of Sam Axe",
                      os.path.join(self._lib, "Burn Notice The Fall of Sam Axe.avi"),
                      2010, 2, 2.2, "someGUID", self._jacket)
        self.assertTrue(movie.matched)

    def test_clean_filename(self):
        movie = Movie(u"abc-:;&%#@def", '123', 2010, 2, 2.2, 'someGUID', 'thumb1')
        self.assertEqual(movie._clean_filename(), 'abc-anddef')

    def test_get_metadata_jacket(self):
        movie = Movie(u"a", 'b', 2010, 2, 2.2, 'c', self._jacket)
        movie.matched = False
        self.assertIsNone(movie.get_metadata_jacket())
        movie.matched = True
        self.assertIsNotNone(movie.get_metadata_jacket())
        h = hashlib.sha1('c').hexdigest()
        self.assertTrue(h[1:] in movie.get_metadata_jacket())

    def test_get_correct_directory(self):
        movie = Movie(u"a", 'b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_directory(), "a (2010)")

    def test_get_correct_filename(self):
        movie = Movie(u"a", 'b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_filename(), "a (2010).avi")

    def test_get_correct_path(self):
        movie = Movie(u"a", 'b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_path(), "a (2010)/a (2010).avi")

    def test_get_correct_absolute_path(self):
        movie = Movie(u"a", '/test/b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_absolute_path(), "/test/a (2010)/a (2010).avi")

    def test_get_correct_absolute_path_with_override(self):
        movie = Movie(u"a", '/test/b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_absolute_path(override='/temp'), "/temp/a (2010)/a (2010).avi")

    def test_str(self):
        movie = Movie(u"a", '/test/b.avi', 2010, 2, 2.2, 'c', self._jacket)
        json_dict = json.loads(str(movie))
        self.assertTrue('fps' in json_dict)
        self.assertTrue('size' in json_dict)
        self.assertTrue('filepath' in json_dict)
        self.assertTrue('title' in json_dict)
        self.assertTrue('correct_title' in json_dict)
        self.assertTrue('title_distance' in json_dict)
        self.assertTrue('year' in json_dict)
        self.assertTrue('matched' in json_dict)
        self.assertTrue('exist' in json_dict)
        self.assertTrue('filename' in json_dict)
        self.assertTrue('jacket' in json_dict)
