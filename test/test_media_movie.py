import unittest
import os
import hashlib
import json
from plexcleaner.media import Movie

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class TestMediaMovie(unittest.TestCase):
    _lib = os.path.join(os.environ['PYTHONPATH'], 'test/library')
    _jacket = 'metadata://com.plexapp.agents.themoviedb_3eb7a03172ea078adbb484ad9d30bfeda4126e2f'
    _metadata_path = 'Library/Application Support/Plex Media Server/Metadata/Movies'
    _jacket_path = "{0}/{1}.bundle/Contents/_stored/{2}"
    _agent_prefix = 'com.plexapp.agents'

    def test_init(self):
        movie = Movie(1, u"Burn Notice: The Fall of Sam Axe",
                      os.path.join(self._lib, 'Burn Notice The Fall of Sam Axe.avi'),
                      2010, 2, 2.2, 'local://1', 'thumb1')
        self.assertFalse(movie.matched)

        movie = Movie(2, u"Burn Notice: The Fall of Sam Axe",
                      os.path.join(self._lib, "Burn Notice The Fall of Sam Axe.avi"),
                      2010, 2, 2.2, "someGUID", self._jacket)
        self.assertTrue(movie.matched)

    def test_clean_filename(self):
        movie = Movie(3, u"abc-:;&%#@def", '123', 2010, 2, 2.2, 'someGUID', 'thumb1')
        self.assertEqual(movie._clean_filename(), 'abc-anddef')

    def test_get_metadata_jacket(self):
        movie = Movie(4, u"a", 'b', 2010, 2, 2.2, 'c', self._jacket)
        movie.matched = False
        self.assertIsNone(movie.get_metadata_jacket())
        movie.matched = True
        self.assertIsNotNone(movie.get_metadata_jacket())
        h = hashlib.sha1('c').hexdigest()
        self.assertTrue(h[1:] in movie.get_metadata_jacket())

    def test_get_metadata_jacket_parsing(self):
        movie = Movie(1, u"a", 'b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(14, len(movie.get_metadata_jacket().split('/')))

    def test_get_correct_directory(self):
        movie = Movie(1, u"a", 'b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_directory(), "a (2010)")

    def test_get_correct_filename(self):
        movie = Movie(2, u"a", 'b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_filename(), "a (2010).avi")

    def test_get_correct_path(self):
        movie = Movie(3, u"a", 'b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_path(), "a (2010)/a (2010).avi")

    def test_get_correct_path_similar(self):
        movie = Movie(3, u"a", 'a (2010)/b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_path(), "a (2010).avi")

    def test_get_correct_absolute_file(self):
        movie = Movie(4, u"a", '/test/b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_absolute_file(), "/test/a (2010)/a (2010).avi")

    def test_get_correct_absolute_file_with_override(self):
        movie = Movie(5, u"a", '/test/b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_absolute_file(override='/temp'), "/temp/a (2010)/a (2010).avi")

    def test_get_correct_absolute_path(self):
        movie = Movie(4, u"a", '/test/b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_absolute_path(), "/test/a (2010)")

    def test_get_correct_absolute_path_similar(self):
        movie = Movie(4, u"a", '/test/a (2010)/b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_absolute_path(), "/test/a (2010)")

    def test_get_correct_absolute_path_with_override(self):
        movie = Movie(5, u"a", '/test/b.avi', 2010, 2, 2.2, 'c', self._jacket)
        self.assertEqual(movie.get_correct_absolute_path(override='/temp'), "/temp/a (2010)")

    def test_str(self):
        movie = Movie(6, u"a", '/test/b.avi', 2010, 2, 2.2, 'c', self._jacket)
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
        self.assertTrue('relative_jacket_path' in json_dict)
        self.assertTrue('original_file' in json_dict)
        self.assertTrue('mid' in json_dict)

if __name__ == '__main__':
    unittest.main()
