__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

import click

plex_home = {
    'type': click.Path(exists=True, dir_okay=True, readable=True, resolve_path=True),
    'default': '/var/lib/plexmediaserver',
    'help': 'Installation location of the Plex Media Server.'
}

new_library = {
    'type': click.Path(exists=True, file_okay=True, dir_okay=True, writable=True, readable=True, resolve_path=True),
    'default': '/mnt/media/video',
    'help': 'Where to consolidate the updated library.'
}

jacket = {
    'type': click.STRING,
    'default': 'poster.jpg',
    'help': 'Name that each movie jacket will have.'
}

database_override = {
    'type': click.Path(exists=True, dir_okay=True, readable=True, resolve_path=True),
    'default': '',
    'help': 'Override the expected Plex Database location.'
}

interrupt = {
    'type': click.BOOL,
    'default': False,
    'is_flag': True,
    'help': 'Interrupt the whole process if a movie file is not found.'
}

log_level = {
    'type': click.Choice(['DEBUG', 'INFO', 'WARNING', 'CRITICAL', 'ERROR']),
    'default': 'DEBUG',
    'help': 'Application verbosity, default is INFO'
}

move_media = {
    'type': click.BOOL,
    'default': False,
    'is_flag': True,
    'help': 'Should the tool move or copy to the new library.'
}