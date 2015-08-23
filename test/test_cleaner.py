import unittest
import subprocess
import re
import errno
import os
import shutil
from plexcleaner.database import Database
from plexcleaner.media import Movie
from testfixtures import log_capture

from plexcleaner import cleaner
from plexcleaner.exception import PlexCleanerException
__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class TestCleaner(unittest.TestCase):
    _BLK_SIZE = 1024
    _KB_TO_B = 1024

    def test_get_free_fs_space(self):
        reg = re.compile("[ ]+")
        output = subprocess.check_output(['df', '-k', '-P', './']).lower()
        actual = dict(zip(reg.split(output.split('\n')[0]), reg.split(output.split('\n')[1])))
        available = self._BLK_SIZE * self._KB_TO_B * int(actual['available'])
        self.assertEqual(available, cleaner.get_free_fs_space('./'))

    @log_capture()
    def test_log_error_EACCES(self, l):
        cleaner.log_error(errno.EACCES, '/')
        self.assertIn('Not enough permission', str(l))

    @log_capture()
    def test_log_error_ENOSPC(self, l):
        cleaner.log_error(errno.ENOSPC, '/')
        self.assertIn('Not enough space', str(l))

    @log_capture()
    def test_log_error_ELSE(self, l):
        cleaner.log_error(errno.ENODATA, '/')
        self.assertIn('Unknown error', str(l))

    @log_capture()
    def test_log_error_ENOENT(self, l):
        cleaner.log_error(errno.ENOENT, '/')
        self.assertIn('Unable to locate', str(l))

    def test_is_plex_running_no_pid_file(self):
        self.assertFalse(cleaner.is_plex_running(pid_file='/PlexMediaServer.pid'))

    def test_is_plex_running_pid_file_with_ok_pid(self):
        self.assertTrue(cleaner.is_plex_running(pid_file='./test/dummy/ok.pid'))

    def test_is_plex_running_pid_file_with_ok_no_perm_pid(self):
        self.assertTrue(cleaner.is_plex_running(pid_file='./test/dummy/ok_no_perm.pid'))

    def test_is_plex_running_pid_file_with_empty_pid(self):
        with self.assertRaises(PlexCleanerException) as e:
            cleaner.is_plex_running(pid_file='./test/dummy/empty.pid')
        self.assertIn('Unable to validate if Plex is running', e.exception.message)

    def test_is_plex_running_pid_file_with_bad_pid(self):
        with self.assertRaises(PlexCleanerException) as e:
            cleaner.is_plex_running(pid_file='./test/dummy/bad.pid')
        self.assertIn('Unable to validate if Plex is running', e.exception.message)

    def test_is_plex_running_pid_file_with_max_pid(self):
        self.assertFalse(cleaner.is_plex_running(pid_file='./test/dummy/max.pid'))

    def test_move_media(self):
        shutil.copy('./test/library/2 Guns.avi', './test/library/abc.avi')
        cleaner.create_dir('./test/library/2 Guns (2009)')
        self.assertTrue(os.path.isdir('./test/library/2 Guns (2009)'))
        moved = cleaner.move_media('./test/library/abc.avi', './test/library/2 Guns (2009)/2 Guns.avi')
        self.assertTrue(os.path.exists('./test/library/2 Guns (2009)/2 Guns.avi'))
        self.assertTrue(moved)

    @log_capture()
    def test_move_media_exist(self, l):
        shutil.copy('./test/library/2 Guns.avi', './test/library/abc.avi')
        cleaner.create_dir('./test/library/2 Guns (2009)')
        self.assertTrue(os.path.isdir('./test/library/2 Guns (2009)'))
        moved = cleaner.move_media('./test/library/abc.avi', './test/library/2 Guns (2009)/2 Guns.avi')
        self.assertIn('already exist', str(l))

    def test_move_media_src_default(self):
        with self.assertRaises(PlexCleanerException) as e:
            moved = cleaner.move_media('./test/library/does_not_exist.avi', './test/library/2 Guns (2009)/2 Guns.avi')
        self.assertTrue('error occurred' in e.exception.message)

    def test_copy_jacket(self):
        cleaner.create_dir('./test/library/2 Guns (2009)')
        self.assertTrue(os.path.isdir('./test/library/2 Guns (2009)'))
        cleaner.copy_jacket('./test/posters/com.plexapp.agents.themoviedb_1a3b1b98c2799d759e110285001f536982cdb869',
                            './test/library/2 Guns (2009)/poster.jpg', False)
        self.assertTrue(os.path.exists('./test/library/2 Guns (2009)/poster.jpg'))

    def test_copy_jacket_skip(self):
        cleaner.create_dir('./test/library/13 (2009)')
        self.assertTrue(os.path.isdir('./test/library/13 (2009)'))
        copied = cleaner.copy_jacket('./test/posters/com.plexapp.agents.themoviedb_1a3b1b98c2799d759e110285001f536982cdb869',
                                     './test/library/13 (2009)/poster.jpg', False)
        self.assertTrue(copied)
        self.assertTrue(os.path.exists('./test/library/13 (2009)/poster.jpg'))
        copied = cleaner.copy_jacket('./test/posters/com.plexapp.agents.themoviedb_1a3b1b98c2799d759e110285001f536982cdb869',
                                     './test/library/13 (2009)/poster.jpg', True)
        self.assertFalse(copied)

    @log_capture()
    def test_copy_jacket_file_missing(self, l):
        cleaner.copy_jacket('./test/posters/missing', './test/library/2 Guns (2009)/poster.jpg', False)
        self.assertTrue(os.path.exists('./test/library/2 Guns (2009)/poster.jpg'))
        self.assertIn('Unable to locate', str(l))

    def test_create_dir(self):
        cleaner.create_dir('./test/library/test_directory')
        self.assertTrue(os.path.isdir('./test/library/test_directory'))

    @log_capture()
    def test_create_dir_exist(self, l):
        cleaner.create_dir('./test/library/test_directory_exist')
        self.assertTrue(os.path.isdir('./test/library/test_directory_exist'))
        cleaner.create_dir('./test/library/test_directory_exist')
        self.assertIn('already exist', str(l))

    def test_create_bad_perm(self):
        cleaner.create_dir('./test/library/test_directory_perm')
        self.assertTrue(os.path.isdir('./test/library/test_directory_perm'))
        os.chmod('./test/library/test_directory_perm', 400)

        with self.assertRaises(PlexCleanerException) as e:
            cleaner.create_dir('./test/library/test_directory_perm/bad')
        self.assertTrue('Unable to create' in e.exception.message)

    def test_update_database(self):
        with Database(database_override='./test/database/com.plexapp.plugins.library.db') as db:
            m = Movie(1, u"a", '/test/b.avi', 2010, 2, 2.2, 'c',
                      './test/posters/com.plexapp.agents.themoviedb_1a3b1b98c2799d759e110285001f536982cdb869')
            before = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (m.mid, )).fetchone()
            cleaner.update_database(db, m, should_update=True)
            after = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (m.mid, )).fetchone()
            self.assertNotEqual(before[0], after[0])
            db.rollback()

    def test_update_database_no_update(self):
        with Database(database_override='./test/database/com.plexapp.plugins.library.db') as db:
            m = Movie(1, u"a", '/test/b.avi', 2010, 2, 2.2, 'c',
                      './test/posters/com.plexapp.agents.themoviedb_1a3b1b98c2799d759e110285001f536982cdb869')
            before = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (m.mid, )).fetchone()
            cleaner.update_database(db, m, should_update=False)
            after = db._cursor.execute('SELECT file FROM media_parts WHERE id = ?', (m.mid, )).fetchone()
            self.assertEqual(before[0], after[0])
