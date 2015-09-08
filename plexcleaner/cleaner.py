import sys
import click
import logging
import os
import signal
import errno
import shutil

from datetime import datetime

from plexcleaner import LOG
from exception import PlexCleanerException
from media import Library
import cli
import database

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class Configuration(object):
    def __init__(self, plex_home, export, update, jacket, interrupt, log_level, database_override, skip_jacket):
        self.plex_home = plex_home
        self.export = export
        self.update = update
        self.jacket = jacket
        self.interrupt = interrupt
        self.log_level = log_level.upper()
        self.database_override = database_override
        self.skip_jacket = skip_jacket


def has_permission(e):
    no_perm = []
    for i in e:
        if not all([os.access(i, os.W_OK), os.access(i, os.R_OK)]):
            no_perm.append(i)

    if no_perm:
        raise PlexCleanerException("Missing Read or Write permission on {0}".format(no_perm), severity=logging.ERROR)

    return True


def backup_database(db):
    backup_time = datetime.now().strftime('.%Y%m%d-%H%M')
    backup = os.path.join(os.path.expanduser('~'), ''.join([os.path.basename(db), backup_time, '.bak']))
    try:
        LOG.info("Creating backup for Plex database at {0}".format(backup))
        shutil.copy(db, backup)
        return True

    except (IOError, OSError) as oe:
        log_error(oe.errno, backup)
        return False


def get_free_fs_space(export):
    statvfs = os.statvfs(export)
    return statvfs.f_frsize * statvfs.f_bavail * 1024


def is_plex_running(pid_file='/var/run/PlexMediaServer.pid'):
    try:
        with open(pid_file) as pf:
            pid = int(pf.read())
            os.kill(int(pid), signal.SIG_DFL)

    except OSError as e:
        if e.errno == errno.ESRCH:
            return False

        elif e.errno == errno.EPERM:
            return True  # The process does not have permission to send the signal to any of the target processes

    except IOError:
        return False

    except (OverflowError, ValueError):
        raise PlexCleanerException('Unable to validate if Plex is running')

    else:
        return True


def log_error(err, dst):
    if err == errno.EACCES:
        LOG.error(u"Not enough permission on: {0}".format(dst))

    elif err == errno.ENOSPC:
        LOG.error(u"Not enough space on destination: {0}".format(os.path.dirname(dst)))

    elif err == errno.ENOENT:
        LOG.error(u"Unable to locate source file to copy to {0}".format(dst))

    else:
        LOG.error(u"Unknown error occurred while executing operation to destination: {0}".format(os.path.dirname(dst)))


def move_media(src, dst, interrupt=False):
    try:
        LOG.debug(u"Copy file '{0}' to '{1}'".format(src, dst))
        if os.path.isfile(dst):
            LOG.debug(u"File '{0}' already exist, will override if not the same file.".format(src))

        shutil.move(src, dst)
        return True

    except (IOError, OSError) as oe:
        log_error(oe.errno, dst)

        if interrupt:
            raise PlexCleanerException('Media movie move error occurred (file missing)', severity=logging.CRITICAL)


def copy_jacket(src, dst, skip):
    try:
        if os.path.isfile(dst) and skip:
            LOG.debug("Jacket '{0}' already exist, skip.".format(dst))
            return False

        shutil.copy(src, dst)
        return True

    except (IOError, OSError) as oe:
        log_error(oe.errno, dst)
        return False


def create_dir(dst):
    try:
        LOG.debug("Creating directory '{0}'.".format(dst))
        os.mkdir(dst)

        return True

    except OSError as e:
        if e.errno == errno.EEXIST:
            LOG.debug("Directory '{0}' already exist.".format(dst))
            return False

        raise PlexCleanerException("Unable to create directory '{0}' check permissions".format(dst),
                                   severity=logging.ERROR)


def update_database(db, m):
    filename = m.get_correct_absolute_file()
    db.update_row(m.mid, filename)
    LOG.debug("Updating movie '{0}' with path '{1}'".format(m.correct_title, filename))
    return True


@click.command()
@click.option('--plex-home', **cli.plex_home)
@click.option('--export', **cli.export)
@click.option('--update/--no-update', **cli.update)
@click.option('--jacket', **cli.jacket)
@click.option('--no-skip-jacket', **cli.no_skip_jacket)
@click.option('--interrupt', **cli.interrupt)
@click.option('--log-level', **cli.log_level)
@click.option('--database-override', **cli.database_override)
def main(**kwargs):
    config = Configuration(**kwargs)
    clean(config)


def clean(config):
    LOG.setLevel(logging.getLevelName(config.log_level))
    try:
        if config.update and is_plex_running():
            raise PlexCleanerException('Should not update database if Plex is running', severity=logging.ERROR)

        with database.Database(metadata_home=config.plex_home, database_override=config.database_override) as db:
            if not backup_database(db.filename):
                raise PlexCleanerException('Unable to create database backup', severity=logging.ERROR)

            library = Library(db)

            if not len(library):
                raise PlexCleanerException('Library is empty', severity=logging.WARNING)

            if library.has_missing_file and config.interrupt:
                raise PlexCleanerException('Missing media file on the filesystem', severity=logging.WARNING)

            if config.export:
                LOG.info("Will consolidate library in: '{0}'".format(config.export))
                has_permission([config.export])
                space = get_free_fs_space(config.export)
                if library.effective_size > space:
                    raise PlexCleanerException('Remaining space on the target filesystem is not enough to export the '
                                               "library {0} Bytes > {1} Bytes".format(library.effective_size, space),
                                               severity=logging.CRITICAL)

            else:
                has_permission(library.library_paths)

            for movie in library:
                LOG.info(u"Processing: '{0}'".format(movie.basename))

                if movie.matched:
                    new_path = movie.get_correct_absolute_path(override=config.export)
                    create_dir(new_path)

                    jacket = os.path.join(new_path, config.jacket)
                    copy_jacket(movie.get_metadata_jacket(metadata_home=config.plex_home), jacket, config.skip_jacket)
                    # TODO: Copy SRT to library

                    moved = move_media(movie.original_file, movie.get_correct_absolute_file(override=config.export),
                                       config.interrupt)
                    if not moved:
                        LOG.info("{0} was not moved to {1}".format(movie.correct_title, new_path))

                    elif config.update and movie.need_update(override=config.export):
                        update_database(db, movie)

                else:
                    LOG.info(u"Movie '{0}' was not matched in Plex".format(movie.basename))

    except PlexCleanerException:
        LOG.error('PlexCleaner did not process media library.')
        sys.exit(1)

    except KeyboardInterrupt:
        LOG.info('bye')
        sys.exit(0)

if __name__ == '__main__':
    main()
