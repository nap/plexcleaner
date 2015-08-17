import sys
import click
import logging
import os
import signal
import errno
import shutil

from plexcleaner import LOG
from exception import PlexCleanerException
from media import Library
import cli
import database

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


def get_free_fs_space(export):
    statvfs = os.statvfs(export)
    return statvfs.f_frsize * statvfs.f_bavail * 1024


def is_plex_running(pid_file='/var/run/PlexMediaServer.pid'):
    try:
        with open(pid_file) as pf:
            pid = int(pf.read())
            os.kill(pid, signal.SIG_DFL)

    except OSError as e:
        if e.errno == errno.ESRCH:
            return False

        elif e.errno == errno.EPERM:
            return True  # The process does not have permission to send the signal to any of the target processes

        else:
            raise PlexCleanerException('Unable to validate if Plex is running')

    except IOError:
        return False

    else:
        return True


def move_media(src, dst):
    try:
        LOG.debug("Copy file '{0}'".format(src))
        if os.path.exists(dst):
            LOG.info("File '{0}' already exist, will override if not the same file.".format(src))
            return False

        shutil.move(src, dst)
        return True

    except shutil.Error as e:
        if 'already exists' in e:
            LOG.warning(e)

        return False

    except (IOError, OSError) as oe:
        if oe.errno == errno.EACCES:
            LOG.error("Not enough permission to edit: {0}".format(dst))

        elif oe.errno == errno.ENOSPC:
            LOG.error("Not enough space on destination: {0}".format(os.path.dirname(dst)))

        else:
            LOG.error("Unknown error occurred while moving media to destination: {0}".format(os.path.dirname(dst)))

        raise PlexCleanerException("Media movie error occurred".format(os.path.dirname(dst)), severity=logging.CRITICAL)


def copy_jacket(src, dst, skip):
    try:
        if os.path.exists(dst) and skip:
            LOG.info("Jacket '{0}' already exist, skip.".format(dst))
            return False

        shutil.copy(src, dst)
        return True

    except shutil.Error as e:
        if 'same file' in e:
            LOG.warning(e)

        return False

    except (IOError, OSError) as oe:
        if oe.errno == errno.EACCES:
            LOG.error("Not enough permission to edit: {0}".format(dst))

        elif oe.errno == errno.ENOSPC:
            LOG.error("Not enough space on destination: {0}".format(os.path.dirname(dst)))

        else:
            LOG.error("Unknown error occurred while copying jacket to destination: {0}".format(os.path.dirname(dst)))

        raise PlexCleanerException("Jacket error occurred".format(os.path.dirname(dst)), severity=logging.ERROR)


def create_dir(dst):
    try:
        if os.path.isdir(dst):
            LOG.info("Directory '{0}' already exist, skip.".format(dst))
            return False

        LOG.info("Creating directory '{0}'.".format(dst))
        os.mkdir(dst)
        return True

    except OSError as e:
        if e.errno == errno.EACCES:
            LOG.info("Directory '{0}' already exist.".format(dst))
            return False

        raise PlexCleanerException("Unable to create directory {0}".format(os.path.basename(dst)),
                                   severity=logging.ERROR)


def clean_dir(dst):
    # TODO: rm dir+jacket if not successful
    # Make sure we don't delete a media file if it was moved
    pass


def update_database(db, m, should_update=False):
    if not should_update:
        LOG.debug('Skipping movie update')
        return False

    filename = m.get_correct_absolute_file()
    db.update_row(m.id, filename)
    LOG.info("Updating movie '{0}' with path '{1}'".format(m.correct_title, filename))


@click.command()
@click.option('--plex-home', **cli.plex_home)
@click.option('--export', **cli.export)
@click.option('--update/--no-update', **cli.update)
@click.option('--jacket', **cli.jacket)
@click.option('--skip-jacket', **cli.skip_jacket)
@click.option('--interrupt', **cli.interrupt)
@click.option('--log-level', **cli.log_level)
@click.option('--database-override', **cli.database_override)
def main(plex_home, export, update, jacket, interrupt, log_level, database_override, skip_jacket):
    LOG.setLevel(logging.getLevelName(log_level.upper()))
    with database.Database(metadata_home=plex_home, database_override=database_override) as db:
        try:
            library = Library(db)

            if not len(library):
                raise PlexCleanerException("Library is empty.", severity=logging.WARNING)

            if library.has_missing_file and interrupt:
                raise PlexCleanerException('Missing media file on the filesystem', severity=logging.WARNING)

            if export:
                LOG.info("Will consolidate library in: '{0}'".format(export))

                free_space = get_free_fs_space(export)
                if library.effective_size > free_space:
                    raise PlexCleanerException('Remaining space on the target filesystem is not enough to export the '
                                               'library {0} Bytes > {1} Bytes'.format(library.effective_size, free_space),
                                               severity=logging.CRITICAL)

            if update and is_plex_running():
                raise PlexCleanerException('Should not update database if Plex is running', severity=logging.ERROR)

            for movie in library:
                LOG.info(u"Processing: '{0}'".format(movie.basename))

                if movie.matched:
                    try:
                        create_dir(movie.get_correct_absolute_path(override=export))
                        media_moved = move_media(movie.original_file, movie.get_correct_absolute_file(override=export))

                        copy_jacket(movie.get_metadata_jacket(),
                                    os.path.join(movie.get_correct_absolute_path(override=export), jacket),
                                    skip_jacket)

                        if media_moved:
                            update_database(db, movie, should_update=update)

                    except Exception:  # TODO: Validate exception case
                        # TODO: log...
                        clean_dir(movie.get_correct_absolute_path(override=export))

                else:
                    LOG.info("Movie '{0}' was not matched in Plex".format(movie.basename))

        except PlexCleanerException as ce:
            print ce.message

        except KeyboardInterrupt:
            LOG.info("bye.")
            sys.exit(0)

if __name__ == '__main__':
    main()
