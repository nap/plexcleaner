__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

import os
import sys
import click
import logging
from subprocess import check_call, CalledProcessError

import cli
from plexcleaner import LOG
from exception import PlexCleanerException, PlexDatabaseException
from media import Library


def copy(src, dst):  # Should allow parallel process call
    try:
        check_call(['cp', '-n', src, dst])

    except CalledProcessError:
        print "Could not copy {0} to {1}".format(src, dst)


@click.command()
@click.option('--plex-home', **cli.plex_home)
@click.option('--new-library', **cli.new_library)
@click.option('--update', **cli.update)
@click.option('--jacket', **cli.jacket)
@click.option('--interrupt', **cli.interrupt)
@click.option('--export', **cli.export)
@click.option('--log-level', **cli.log_level)
@click.option('--database-override', **cli.database_override)
def main(plex_home, new_library, update, jacket, interrupt, export, log_level, database_override):
    LOG.setLevel(logging.getLevelName(log_level.upper()))

    try:
        library = Library(metadata_home=plex_home, database_override=database_override)

        if not len(library):
            raise PlexCleanerException("Library is empty.")

        for movie in library:
            LOG.info(u"Processing: {0}".format(movie.safe_title))

            media_directory = movie.get_new_path(new_library)
            if not os.path.isdir(media_directory):
                LOG.info(u"Creating directory '{0}' in {1}".format(movie.get_formatted_directory(), new_library))
                # TODO: os.mkdir(media_directory)

            media_poster = os.path.join(media_directory, jacket)
            if os.path.isfile(media_poster):
                LOG.warning(u"Poster '{0}' is already in target library".format(media_poster))

            else:
                LOG.info(u"Copying poster '{0}' in '{1}'".format(jacket, media_directory))

            media_file = movie.get_new_filename(new_library)
            if os.path.exists(media_file):
                LOG.warning(u"Movie '{0}' is already in target library {1}".format(media_file, new_library))

            else:
                LOG.info(u"Copying movie '{0}' in '{1}'".format(movie.get_formatted_file(), media_directory))

    except PlexDatabaseException as de:
        print de.message

    except PlexCleanerException as ce:
        print ce.message

    except KeyboardInterrupt:
        LOG.info("bye.")
        sys.exit(0)

if __name__ == '__main__':
    main()
