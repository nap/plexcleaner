import unittest
import subprocess
import re

from plexcleaner import cleaner
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

    def test_is_plex_running(self):
        #def is_plex_running(pid_file='/var/run/PlexMediaServer.pid'):
        pass

    def test_log_error(self):
        #def log_error(err, dst):
        pass

    def test_move_media(self):
        #def move_media(src, dst):
        pass

    def test_copy_jacket(self):
        #def copy_jacket(src, dst, skip):
        pass

    def test_copy_jacket_skpi(self):
        #def copy_jacket(src, dst, skip):
        pass

    def test_creatE_dir(self):
        #def create_dir(dst):
        pass

    def test_update_database(self):
        #def update_database(db, m, should_update=False):
        pass

    def test_update_database_no_update(self):
        #def update_database(db, m, should_update=False):
        pass