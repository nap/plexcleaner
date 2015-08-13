from plexcleaner import LOG, log_severity
__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'


class PlexCleanerException(Exception):
    def __init__(self, *args, **kwargs):
        super(Exception, self).__init__(args[0])

        log = LOG.debug
        if 'severity' in kwargs and kwargs['severity'] in log_severity:
            log = getattr(LOG, log_severity[kwargs['severity']])

        log(args[0])
