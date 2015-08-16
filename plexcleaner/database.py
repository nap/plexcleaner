import sqlite3
import os
import logging

from plexcleaner import LOG
from exception import PlexCleanerException

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class Database(object):
    _database_path = 'Library/Application Support/Plex Media Server/Plug-in Support/Databases'
    _update_movie = 'UPDATE media_parts SET file = ? WHERE id = ?'
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
                LOG.debug("User database override {0}".format(database))

            with sqlite3.connect(database) as conn:
                self._connection = conn
                self._cursor = conn.cursor()

        except sqlite3.OperationalError:
            raise PlexCleanerException("Could not connect to Plex database: {0}".format(database),
                                       severity=logging.WARNING)

    def get_rows(self):
        return self._cursor.execute(''.join(self._select_movies))

    def update_row(self, mid, value):
        LOG.debug("Updating movie '{0}' with '{1}'".format(mid, value))
        self._cursor.execute(self._update_movie, (value, mid))

    def update_many_row(self, values):
        LOG.debug("Updating {0} movies".format(len(values)))
        self._cursor.executemany(self._update_movie, values)
        self.commit()

    def commit(self):
        LOG.debug('Commiting last changes to database.')
        self._connection.commit()

    def rollback(self):
        LOG.debug('Rollback last changes to database.')
        self._connection.rollback()
