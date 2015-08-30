import sys
import click
import logging
import os
import signal
import errno
import shutil
import pwd

from plexcleaner import LOG
from exception import PlexCleanerException
from media import Library
import cli
import database

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


def check_permission(db):
    current_user = pwd.getpwuid(os.geteuid()).pw_name
    return all([
        current_user in ['root', 'plex'],
        os.access(db, os.W_OK),
        os.access(db, os.R_OK)
    ])


def backup_database(db):
    backup = os.path.join(os.path.expanduser('~'), ''.join([os.path.basename(db), '.bak']))
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
        LOG.error("Not enough permission on: {0}".format(dst))

    elif err == errno.ENOSPC:
        LOG.error("Not enough space on destination: {0}".format(os.path.dirname(dst)))

    elif err == errno.ENOENT:
        LOG.error("Unable to locate source file to copy to {0}".format(dst))

    else:
        LOG.error("Unknown error occurred while executing operation to destination: {0}".format(os.path.dirname(dst)))


def move_media(src, dst):
    try:
        LOG.debug("Copy file '{0}' to '{1}'".format(src, dst))
        if os.path.isfile(dst):
            LOG.info("File '{0}' already exist, will override if not the same file.".format(src))

        shutil.move(src, dst)
        return True

    except (IOError, OSError) as oe:
        log_error(oe.errno, dst)
        raise PlexCleanerException('Media movie error occurred', severity=logging.CRITICAL)


def copy_jacket(src, dst, skip):
    try:
        if os.path.isfile(dst) and skip:
            LOG.info("Jacket '{0}' already exist, skip.".format(dst))
            return False

        shutil.copy(src, dst)
        return True

    except (IOError, OSError) as oe:
        log_error(oe.errno, dst)
        return False


def create_dir(dst):
    try:
        LOG.info("Creating directory '{0}'.".format(dst))
        os.mkdir(dst)
        return True

    except OSError as e:
        if e.errno == errno.EEXIST:
            LOG.info("Directory '{0}' already exist.".format(dst))
            return False

        raise PlexCleanerException("Unable to create directory '{0}'".format(dst), severity=logging.ERROR)


def update_database(db, m, should_update=False):
    if not should_update:
        LOG.debug('Skipping movie update')
        return False

    if m.need_update():
        filename = m.get_correct_absolute_file()
        db.update_row(m.mid, filename)
        LOG.info("Updating movie '{0}' with path '{1}'".format(m.correct_title, filename))
        return True

    LOG.debug("Movie {0} did not change location, database will not be updated.")
    return False


@click.command()
@click.option('--plex-home', **cli.plex_home)
@click.option('--export', **cli.export)
@click.option('--update/--no-update', **cli.update)
@click.option('--jacket', **cli.jacket)
@click.option('--skip-jacket', **cli.skip_jacket)
@click.option('--interrupt', **cli.interrupt)
@click.option('--log-level', **cli.log_level)
@click.option('--database-override', **cli.database_override)
def clean(plex_home, export, update, jacket, interrupt, log_level, database_override, skip_jacket):
    LOG.setLevel(logging.getLevelName(log_level.upper()))
    with database.Database(metadata_home=plex_home, database_override=database_override) as db:
        try:
            if not check_permission(db):
                raise PlexCleanerException("Unable to open database, permission denied, located at: {0}".format(db),
                                           severity=logging.ERROR)

            if not backup_database(db):
                raise PlexCleanerException('Unable to create database backup', severity=logging.ERROR)

            library = Library(db)

            if not len(library):
                raise PlexCleanerException("Library is empty.", severity=logging.WARNING)

            if library.has_missing_file and interrupt:
                raise PlexCleanerException('Missing media file on the filesystem', severity=logging.WARNING)

            if export:
                LOG.info("Will consolidate library in: '{0}'".format(export))

                space = get_free_fs_space(export)
                if library.effective_size > space:
                    raise PlexCleanerException('Remaining space on the target filesystem is not enough to export the '
                                               'library {0} Bytes > {1} Bytes'.format(library.effective_size, space),
                                               severity=logging.CRITICAL)

            if update and is_plex_running():
                raise PlexCleanerException('Should not update database if Plex is running', severity=logging.ERROR)

            for movie in library:
                LOG.info(u"Processing: '{0}'".format(movie.basename))

                if movie.matched:
                    new_path = movie.get_correct_absolute_path(override=export)
                    create_dir(new_path)

                    media_moved = move_media(movie.original_file, movie.get_correct_absolute_file(override=export))
                    if media_moved:
                        new_jacket = os.path.join(new_path, jacket)
                        copy_jacket(movie.get_metadata_jacket(metadata_home=plex_home), new_jacket, skip_jacket)
                        # TODO: Copy SRT to library

                        if movie.need_update(export=export):
                            update_database(db, movie, should_update=update)

                    else:
                        LOG.warning("Unable to move {0} to {1}".format(movie.correct_title, new_path))

                else:
                    LOG.info("Movie '{0}' was not matched in Plex".format(movie.basename))

        except PlexCleanerException:
            LOG.error('PlexCleaner did not process media library.')
            sys.exit(1)

        except KeyboardInterrupt:
            LOG.info("bye.")
            sys.exit(0)

if __name__ == '__main__':
    clean()
