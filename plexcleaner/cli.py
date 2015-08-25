import click
from plexcleaner import log_severity

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

plex_home = {
    'type': click.Path(exists=True, dir_okay=True, readable=True, resolve_path=True),
    'default': '/var/lib/plexmediaserver',
    'show_default': True,
    'help': 'Installation location of the Plex Media Server.'
}

export = {
    'type': click.Path(exists=True, file_okay=True, dir_okay=True, writable=True, readable=True, resolve_path=True),
    'default': None,
    'help': 'Move the updated library format in a new folder.'
}

update = {
    'default': True,
    'is_flag': True,
    'help': 'Update Plex database with renamed and moved media.'
}

jacket = {
    'type': click.STRING,
    'default': 'poster.jpg',
    'show_default': True,
    'help': 'Name that each movie jacket will have.'
}

database_override = {
    'type': click.Path(exists=True, dir_okay=True, readable=True, resolve_path=True),
    'default': None,
    'help': 'Override the expected Plex Database location.'
}

log_level = {
    'type': click.Choice(log_severity.values()),
    'default': 'info',
    'help': 'Application verbosity, default is INFO'
}

interrupt = {
    'type': click.BOOL,
    'default': False,
    'is_flag': True,
    'help': 'Interrupt the whole process if a movie file is not found on the filesystem.'
}

skip_jacket = {
    'default': True,
    'is_flag': True,
    'help': 'Should the copy of movie jacket be skipped if it\'s already present.'
}
