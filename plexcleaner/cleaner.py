__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

import sys
import click
import logging

import cli
from plexcleaner import LOG
from exception import PlexCleanerException, PlexDatabaseException
from media import Library


@click.command()
@click.option('--plex-home', **cli.plex_home)
@click.option('--export', **cli.export)
@click.option('--update', **cli.update)
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

        if export:
            LOG.info("Will consolidate library in: '{0}'".format(export))

        for movie in library:
            LOG.info(u"Processing: {0}".format(movie.correct_title))

    except PlexDatabaseException as de:
        print de.message

    except PlexCleanerException as ce:
        print ce.message

    except KeyboardInterrupt:
        LOG.info("bye.")
        sys.exit(0)

if __name__ == '__main__':
    main()
