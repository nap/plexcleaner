import sqlite3
import os
import logging

from plexcleaner import LOG
from exception import PlexCleanerException

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class Database(object):
    _uncommited = False
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
        db = os.path.join(metadata_home, self._database_path, database_name)
        try:
            if database_override:
                db = database_override
                LOG.debug("User database override {0}".format(db))

            LOG.info("Reading Plex database located at {0}".format(db))
            self._connection = sqlite3.connect(db)
            self._cursor = self._connection.cursor()

        except sqlite3.OperationalError:
            raise PlexCleanerException("Could not connect to Plex database: {0}".format(db), severity=logging.ERROR)

        except sqlite3.DatabaseError as de:
            raise PlexCleanerException("Could not open Plex database: {0}".format(de.message), severity=logging.ERROR)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._uncommited:
            self.commit()

        self._connection.close()

    def get_rows(self):
        try:
            return self._cursor.execute(''.join(self._select_movies))

        except sqlite3.DatabaseError as de:
            raise PlexCleanerException("Unabled to fetch database rows {0}".format(de.message), severity=logging.ERROR)

    def update_row(self, mid, value):
        LOG.debug("Updating movie '{0}' with '{1}'".format(mid, value))
        self._cursor.execute(self._update_movie, (value, mid))
        self._uncommited = True

    def update_many_row(self, values):
        LOG.debug("Updating {0} movies".format(len(values)))
        self._cursor.executemany(self._update_movie, values)
        self._uncommited = True

    def commit(self):
        LOG.debug('Commiting last changes to database.')
        try:
            self._connection.commit()
            self._uncommited = False

        except sqlite3.DatabaseError as de:
            LOG.error("Unable to commit changes to database: {0}".format(de.message))

    def rollback(self):
        LOG.debug('Rollback last changes to database.')
        try:
            self._connection.rollback()
            self._uncommited = False

        except sqlite3.DatabaseError as de:
            LOG.error("Unable unable to rollback uncommited changes: {0}".format(de.message))

    def has_uncommited(self):
        return self._uncommited
