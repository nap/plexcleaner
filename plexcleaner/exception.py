from plexcleaner import LOG

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class PlexCleanerException(Exception):
    def __init__(self, message, **kwargs):
        super(Exception, self).__init__(message, **kwargs)
        LOG.debug(message)


class PlexDatabaseException(PlexCleanerException):
    pass


class PlexMediaFileException(PlexCleanerException):
    pass


class PlexOSException(PlexCleanerException):
    pass
