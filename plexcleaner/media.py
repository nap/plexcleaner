__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

import unicodedata
import string
import sqlite3
import os
import hashlib
from pyjarowinkler import distance

from exception import PlexDatabaseException


class Library(object):
    _database_path = 'Library/Application Support/Plex Media Server/Plug-in Support/Databases'
    _select_movies = (
        'SELECT metadata_items.title, media_parts.file, metadata_items.year, ',
        'metadata_items.guid, metadata_items.user_thumb_url FROM media_items ',
        'JOIN metadata_items ON media_items.metadata_item_id = metadata_items.id ',
        'JOIN media_parts ON media_parts.media_item_id = media_items.id'
    )

    def __init__(self,
                 database_name='com.plexapp.plugins.library.db',
                 metadata_home='/var/lib/plexmediaserver',
                 database_override=None):

        self.library = dict()
        self.unmatched = dict()
        self.effective_size = 0
        database = os.path.join(metadata_home, self._database_path, database_name)
        try:
            if database_override:
                database = database_override

            with sqlite3.connect(database) as conn:
                cursor = conn.cursor()

                for row in cursor.execute(''.join(self._select_movies)):
                    movie = Movie(*row, metadata_home=metadata_home)

                    if movie.has_poster:  # If a poster was synced, this means that the movie was matched in Plex
                        self.library.update({movie.title: movie})

                        if movie.exist:
                            self.effective_size += movie.size

                    self.unmatched.update({movie.title: movie})

        except sqlite3.OperationalError:
            raise PlexDatabaseException("Could not connect to Plex database\n{0}".format(database))

    def __iter__(self):
        return self.library.iteritems()

    def __len__(self):
        return len(self.library)


class Movie(object):
    _metadata_path = 'Library/Application Support/Plex Media Server/Metadata/Movies'
    _poster_path = "{0}/{1}.bundle/Contents/_stored/{2}"

    def __init__(self, title, filename, year, guid, poster, metadata_home='/var/lib/plexmediaserver',
                 default_poster='thumb1'):
        self.metadata_home = metadata_home
        self.default_poster = default_poster
        self.file = filename
        self.filepath = os.path.dirname(filename)
        self.filename, self.file_ext = os.path.splitext(os.path.basename(filename))
        self.title = title
        self.safe_title = self._clean_filename()
        self.title_distance = distance.get_jaro_distance(self.title, self.safe_title)
        self.year = year
        self.exist = os.path.exists(filename)
        self.size = os.stat(self.file).st_size if self.exist else 0
        self.guid = guid
        parent_path, child_path = self._get_hash()[0], self._get_hash()[1]
        self.poster = self._poster_path.format(parent_path, child_path, poster[11:])  # Remove metadata://

    def _clean_filename(self, replacements=None):
        if not replacements:
            replacements = [('&', 'and')]

        cleaned = unicodedata.normalize('NFKD', self.title).encode('ASCII', 'ignore')
        for r in replacements:
            cleaned = cleaned.replace(*r)

        return ''.join(char for char in cleaned if char in "-_.()' {0}{1}".format(string.ascii_letters, string.digits))

    def has_poster(self):
        return self.default_poster not in self.poster

    def get_formatted_directory(self):
        return "{0} ({1})".format(self.safe_title, self.year)

    def get_formatted_file(self):
        return "{0} ({1}){2}".format(self.safe_title, self.year, self.file_ext)

    def get_new_filename(self, new_library):
        return os.path.join(new_library, self.get_formatted_directory(), self.get_formatted_file())

    def get_new_path(self, new_library):
        return os.path.join(new_library, self.get_formatted_directory())

    def _get_hash(self):
        return hashlib.sha1(self.guid).hexdigest()

    def as_dict(self):
        return str({
            self.title: {
                'filename': self.filename,
                'filepath': self.filepath,
                'exist': self.exist,
                'file': self.file,
                'size': self.size,
                'title_distance': self.title_distance,
                'safe_title': self.safe_title,
                'file_ext': self.file_ext[1:],
                'formatted_file': self.get_formatted_file(),
                'formatted_directory': self.get_formatted_directory(),
                'poster': os.path.join(self.metadata_home, self._metadata_path, self.poster)
            }
        })

