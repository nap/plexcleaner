import sys
import click
import logging
import os
import shutil
import signal
import errno

import cli
from plexcleaner import LOG
from exception import PlexCleanerException, PlexDatabaseException, PlexMediaFileException, PlexOSException
from media import Library

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


def get_free_fs_space(export):
    statvfs = os.statvfs(export)
    avail_size = statvfs.f_frsize * statvfs.f_bavail
    return avail_size * 1024


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
            raise PlexOSException('Unable to validate if Plex is running')

    except IOError:
        return False

    else:
        return True


@click.command()
@click.option('--plex-home', **cli.plex_home)
@click.option('--export', **cli.export)
@click.option('--update/--no-update', **cli.update)
@click.option('--jacket', **cli.jacket)
@click.option('--interrupt', **cli.interrupt)
@click.option('--log-level', **cli.log_level)
@click.option('--database-override', **cli.database_override)
def main(plex_home, export, update, jacket, interrupt, log_level, database_override):
    LOG.setLevel(logging.getLevelName(log_level.upper()))

    try:
        library = Library(metadata_home=plex_home, database_override=database_override)

        if not len(library):
            raise PlexCleanerException("Library is empty.")

        if library.has_missing_file and interrupt:
            raise PlexMediaFileException('Missing media file on the filesystem')

        if export:
            LOG.info("Will consolidate library in: '{0}'".format(export))

            free_space = get_free_fs_space(export)
            if library.effective_size > free_space:
                LOG.critical('Not enough space: {0} Bytes > {1} Bytes'.format(library.effective_size, free_space))
                raise PlexOSException('Remaining space on the target filesystem is not enough to export the library')

        if update and is_plex_running():
            LOG.critical('Cannot update media file location if Plex is running')
            raise PlexOSException('Should not update database if Plex is running')

        for movie in library:
            LOG.info(u"Processing: '{0}'".format(movie.basename))
            # TODO: Multiprocess shutil.move()
            # TODO: Copy jacket
            # TODO: Update database

    except PlexDatabaseException as de:
        print de.message

    except PlexMediaFileException as fe:
        print fe.message

    except PlexOSException as oe:
        print oe.message

    except PlexCleanerException as ce:
        print ce.message

    except KeyboardInterrupt:
        LOG.info("bye.")
        sys.exit(0)

if __name__ == '__main__':
    main()
