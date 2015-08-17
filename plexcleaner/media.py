import unicodedata
import string
import os
import hashlib
import json

from pyjarowinkler import distance
import unidecode

from plexcleaner import LOG

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class Library(object):
    _B_TO_GB = 9.3132257461547852e-10
    # TODO: Figureout what media_items.deleted_at implies

    def __init__(self, db):
        self.library = []
        self.effective_size = 0
        self.has_missing_file = False

        for row in db.get_rows():
            movie = Movie(*row)
            self._update_library(movie)

        LOG.info("Library size is {0:0.3f} gigabyte".format(self.effective_size * self._B_TO_GB))

    def _update_library(self, movie):
        self.library.append(movie)

        if movie.exist and movie.matched:  # Movie might be in the database but it might be absent in the filesystem
            self.effective_size += movie.size

        if not movie.exist:
            self.has_missing_file = True
            LOG.warning("The file {0} is missing".format(movie.original_file))

    def __iter__(self):
        for m in self.library:
            yield m

    def __len__(self):
        return len(self.library)


class Movie(object):
    """ Describe movie file as it can be found in the Plex Database
    """
    _metadata_path = 'Library/Application Support/Plex Media Server/Metadata/Movies'
    _jacket_path = "{0}/{1}.bundle/Contents/_stored/{2}"

    def __init__(self, mid, title, original_file, year, size, fps, guid, jacket):
        self.mid = mid
        self.original_file = original_file
        self.filepath = os.path.dirname(original_file)
        self.basename = os.path.basename(original_file)
        self.filename, self.file_ext = os.path.splitext(self.basename)

        self.title = title
        self.correct_title = self._clean_filename()
        self.title_distance = distance.get_jaro_distance(self.title, self.correct_title)

        self.year = year
        self.size = size
        self.fps = fps
        self.exist = os.path.exists(original_file)
        self.matched = not guid.startswith('local://')

        if self.matched:
            h = hashlib.sha1(guid).hexdigest()
            self.jacket = os.path.join(self._metadata_path, self._jacket_path.format(h[0], h[1:], jacket[11:]))

    def _clean_filename(self, replacements=None):
        if not replacements:
            replacements = [('&', 'and')]

        cleaned = unidecode.unidecode(self.title)
        for r in replacements:
            cleaned = cleaned.replace(*r)

        return ''.join(char for char in cleaned if char in "-_.()' {0}{1}".format(string.ascii_letters, string.digits))

    def get_correct_directory(self):
        return "{0} ({1})".format(self.correct_title, self.year)

    def get_correct_filename(self):
        return "{0} ({1}){2}".format(self.correct_title, self.year, self.file_ext)

    def get_correct_path(self):
        return os.path.join(self.get_correct_directory(), self.get_correct_filename())

    def get_correct_absolute_file(self, override=None):  # parent is for move the file to a new location
        if not override:
            return os.path.join(self.filepath, self.get_correct_path())

        return os.path.join(override, self.get_correct_path())

    def get_correct_absolute_path(self, override=None):
        directory = "{0} ({1})".format(self.correct_title, self.year)
        if not override:
            return os.path.join(self.filepath, directory)

        return os.path.join(override, directory)

    def get_metadata_jacket(self, metadata_home='/var/lib/plexmediaserver'):
        if not self.matched:
            return None

        return os.path.join(metadata_home, self._metadata_path, self.jacket)

    def __str__(self):
        serialized = dict()
        attributes = [a for a in dir(self) if not a.startswith('_')]

        for attribute in attributes:
            if callable(self.__getattribute__(attribute)):
                serialized.update({attribute.replace('get_', ''): getattr(self, attribute)()})

            else:
                serialized.update({attribute: self.__getattribute__(attribute)})

        return json.dumps(serialized)
