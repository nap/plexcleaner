__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

import unicodedata
import string
import sqlite3
import os
import hashlib
import json
from pyjarowinkler import distance

from exception import PlexDatabaseException


class Library(object):
    _database_path = 'Library/Application Support/Plex Media Server/Plug-in Support/Databases'
    # TODO: Figureout what media_items.deleted_at implies
    _select_movies = (
        'SELECT metadata_items.title, media_parts.file, metadata_items.year, ',
        'media_parts.size, media_items.frames_per_second AS fps, '
        'metadata_items.guid, metadata_items.user_thumb_url AS jacket FROM media_items ',
        'JOIN metadata_items ON media_items.metadata_item_id = metadata_items.id ',
        'JOIN media_parts ON media_parts.media_item_id = media_items.id'
    )

    def __init__(self,
                 database_name='com.plexapp.plugins.library.db',
                 metadata_home='/var/lib/plexmediaserver',
                 database_override=None):

        self.library = []
        self.effective_size = 0

        database = os.path.join(metadata_home, self._database_path, database_name)
        try:
            if database_override:
                database = database_override

            with sqlite3.connect(database) as conn:
                cursor = conn.cursor()

                for row in cursor.execute(''.join(self._select_movies)):
                    movie = Movie(*row)
                    self._update_library(movie)

        except sqlite3.OperationalError:
            raise PlexDatabaseException("Could not connect to Plex database: {0}".format(database))

    def _update_library(self, movie):
        self.library.append(movie)

        if movie.exist and movie.matched:  # Movie might be in the database but it might be absent in the filesystem
            self.effective_size += movie.size

    def get_library(self):
        return self.library

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
    _default_jacket = "thumb1"

    def __init__(self, title, absolute_file, year, size, fps, guid, jacket):
        self.filepath = os.path.dirname(absolute_file)
        self.filename, self.file_ext = os.path.splitext(os.path.basename(absolute_file))

        self.title = title
        self.correct_title = self._clean_filename()
        self.title_distance = distance.get_jaro_distance(self.title, self.correct_title)

        self.year = year
        self.size = size
        self.fps = fps
        self.exist = os.path.exists(absolute_file)
        self.matched = self._default_jacket not in jacket

        if self.matched:
            h = hashlib.sha1(guid).hexdigest()
            self.jacket = os.path.join(self._metadata_path, self._jacket_path.format(h[0], h[1], jacket[11:]))

    def _clean_filename(self, replacements=None):
        if not replacements:
            replacements = [('&', 'and')]

        cleaned = unicodedata.normalize('NFKD', self.title).encode('ASCII', 'ignore')
        for r in replacements:
            cleaned = cleaned.replace(*r)

        return ''.join(char for char in cleaned if char in "-_.()' {0}{1}".format(string.ascii_letters, string.digits))

    def get_correct_directory(self):
        return "{0} ({1})".format(self.correct_title, self.year)

    def get_correct_filename(self):
        return "{0} ({1}){2}".format(self.correct_title, self.year, self.file_ext)

    def get_correct_path(self):
        return os.path.join(self.get_correct_directory(), self.get_correct_filename())

    def get_correct_absolute_path(self, parent=None):  # parent is for move the file to a new location
        if not parent:
            return os.path.join(self.filepath, self.get_correct_path())

        return os.path.join(parent, self.get_correct_path())

    def get_metadata_jacket(self):
        if not self.matched:
            return None

        return os.path.join(self._metadata_path, self.jacket)

    def __str__(self):
        serialized = dict()
        attributes = [a for a in dir(self) if not a.startswith('_')]

        for attribute in attributes:
            if callable(self.__getattribute__(attribute)):
                serialized.update({attribute.replace('get_', ''): getattr(self, attribute)()})

            else:
                serialized.update({attribute: self.__getattribute__(attribute)})

        return json.dumps(serialized)
