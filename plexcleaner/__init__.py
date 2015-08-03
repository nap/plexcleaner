__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

from exception import PlexMediaFileException, PlexDatabaseException, PlexCleanerException
from media import Library

import logging

LOG = logging.getLogger(__name__)
log_config = {
    'format': '%(asctime)s %(name)-6s %(levelname)-6s %(message)s',
    'handler': logging.StreamHandler(),
    'level': logging.DEBUG
}
logging.basicConfig(**log_config)
