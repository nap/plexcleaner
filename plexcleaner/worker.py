__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'
from Queue import Queue


class Worker(object):
    def __init__(self, library):
        self.queue = Queue(len(library))

