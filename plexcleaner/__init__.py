import logging

__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

LOG = logging.getLogger(__name__)
log_config = {
    'format': '%(asctime)s %(name)-6s %(levelname)-6s %(message)s',
    'handler': logging.StreamHandler(),
    'level': logging.DEBUG
}
logging.basicConfig(**log_config)

log_severity = {
    10: 'debug',
    20: 'info',
    30: 'warning',
    50: 'critical',
    40: 'error'
}
