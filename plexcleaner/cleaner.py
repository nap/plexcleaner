import sys
import click
import logging
import os
import signal
import errno
import shutil

import cli
from plexcleaner import LOG
from exception import PlexCleanerException
from media import Library

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
    # TODO: Handle unicode
    # TODO: Exceptions
    if not os.path.exists(dst):
        shutil.move(src, dst)

    LOG.info("File {0} already exist, will rename/override.")


def copy_jacket(src, dst, skip):
    if not os.path.exists(dst) and not skip:
        shutil.copy(src, dst)

    LOG.info("Jacket {0} already exist, skip.")


def create_dir(dst):
    # TODO: Handle unicode
    # TODO: Exceptions
    if not os.path.isdir(dst):
        os.mkdir(dst)

    LOG.info("Directory {0} already exist, skip.")


def clean_dir(dst):
    # TODO: rm dir+jacket if not successful
    # Make sure we don't delete a media file if it was moved
    pass


def update_database(id, dst):
    # TODO: Get database instance
    # TODO: Update row id with dst value
    pass


@click.command()
@click.option('--plex-home', **cli.plex_home)
@click.option('--export', **cli.export)
@click.option('--update/--no-update', **cli.update)
@click.option('--jacket', **cli.jacket)
@click.option('--interrupt', **cli.interrupt)
@click.option('--log-level', **cli.log_level)
@click.option('--database-override', **cli.database_override)
def main(plex_home, export, update, jacket, interrupt, log_level, database_override, skip_jacket):
    LOG.setLevel(logging.getLevelName(log_level.upper()))

    try:
        library = Library(metadata_home=plex_home, database_override=database_override)

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
            LOG.critical('Cannot update media file location if Plex is running')
            raise PlexCleanerException('Should not update database if Plex is running', severity=logging.ERROR)

        for movie in library:
            LOG.info(u"Processing: '{0}'".format(movie.basename))
            if movie.matched:
                try:
                    create_dir(movie.get_correct_absolute_path(override=export))
                    # TODO: Delete following line
                    test = os.path.join('./test/posters', os.path.basename(movie.get_metadata_jacket()))  # FOR TESTING
                    copy_jacket(test, os.path.join(movie.get_correct_absolute_path(override=export), jacket), skip_jacket)
                    move_media(movie.original_file, movie.get_correct_absolute_file(override=export))
                    update_database(movie.id, movie.get_correct_absolute_file(override=export))

                except Exception:  # TODO: Validate exception case
                    # TODO: log...
                    clean_dir(movie.get_correct_absolute_path(override=export))
                    pass
            else:
                LOG.info("Movie '{0}' was not matched in Plex".format(movie.basename))

    except PlexCleanerException as ce:
        print ce.message

    except KeyboardInterrupt:
        LOG.info("bye.")
        sys.exit(0)

if __name__ == '__main__':
    main()
