__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

import os
import sys
import click
import logging
from subprocess import check_call, CalledProcessError

import cli
from plexcleaner import LOG, Library, PlexDatabaseException, PlexCleanerException


def copy(src, dst):  # Should allow parallel process call
    try:
        check_call(['cp', '-n', src, dst])

    except CalledProcessError:
        print "Could not copy {0} to {1}".format(src, dst)


@click.command()
@click.option('--plex-home', **cli.plex_home)
@click.option('--new-library', **cli.new_library)
@click.option('--jacket', **cli.jacket)
@click.option('--database-override', **cli.database_override)
@click.option('--interrupt', **cli.interrupt)
@click.option('--log-level', **cli.log_level)
@click.option('--move-media', **cli.move_media)
def main(plex_home, new_library, jacket, database_override, interrupt, log_level, move_media):
    LOG.setLevel(logging.getLevelName(log_level.upper()))

    try:
        library = Library(metadata_home=plex_home, database_override=database_override)

        if not len(library):
            raise PlexCleanerException("Library is empty.")

        for title, movie in library:
            LOG.info(u"Processing: {0}".format(title))

            media_directory = movie.get_new_path(new_library)
            if not os.path.isdir(media_directory):
                LOG.debug(u"Creating directory '{0}' in {1}".format(media_directory, new_library))
                # TODO: os.mkdir(media_directory)

            media_poster = os.path.join(media_directory, jacket)
            if os.path.isfile(media_poster):
                LOG.debug(u"Poster '{0}' is already in target library".format(media_poster))

            else:
                LOG.debug(u"Copying movie '{0}' in '{1}'".format(jacket, media_directory))

            media_file = movie.get_new_filename(new_library)
            if os.path.exists(media_file):
                LOG.debug(u"Movie '{0}' is already in target library {1}".format(media_file, new_library))

            else:
                LOG.debug(u"Copying movie '{0}' in '{1}'".format(movie.get_formatted_file(), new_library))

    except PlexDatabaseException as de:
        print de.message

    except PlexCleanerException as ce:
        print ce.message

    except KeyboardInterrupt:
        print "bye."
        sys.exit(0)

if __name__ == '__main__':
    main()
