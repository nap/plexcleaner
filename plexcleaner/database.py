import sqlite3
import os
import logging

from exception import PlexCleanerException

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class Database(object):
    _database_path = 'Library/Application Support/Plex Media Server/Plug-in Support/Databases'
    _update_movie = "UPDATE media_parts SET media_parts.file = ? WHERE media_parts.id = ?"
    _select_movies = (
        'SELECT media_parts.id, metadata_items.title, media_parts.file, metadata_items.year, ',
        'media_parts.size, media_items.frames_per_second AS fps, '
        'metadata_items.guid, metadata_items.user_thumb_url AS jacket FROM media_items ',
        'JOIN metadata_items ON media_items.metadata_item_id = metadata_items.id ',
        'JOIN media_parts ON media_parts.media_item_id = media_items.id'
    )

    # TODO: add logging
    def __init__(self, metadata_home='/var/lib/plexmediaserver',
                 database_override=None, database_name='com.plexapp.plugins.library.db'):
        database = os.path.join(metadata_home, self._database_path, database_name)
        try:
            if database_override:
                database = database_override

            with sqlite3.connect(database) as conn:
                self.cursor = conn.cursor()

        except sqlite3.OperationalError:
            raise PlexCleanerException("Could not connect to Plex database: {0}".format(database),
                                       severity=logging.WARNING)

    def get_rows(self):
        return self.cursor.execute(''.join(self._select_movies))

    def update_row(self, mid, value):
        self.cursor.execute(self._update_movie, (mid, value))

    def update_many_row(self, values):
        self.cursor.executemany(self._update_movie, values)
