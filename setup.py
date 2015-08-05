__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'
__version__ = '0.0.1'

import os
import sys
from setuptools import setup, find_packages


if sys.version_info[:2] < (2, 7):
    raise RuntimeError('plexcelaner requires Python 2.7 minimum (untested on python 3)')


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup_info = {
    'name': 'plexcleaner',
    'version': __version__,
    'maintainer': __author__.split(' - ')[0],
    'maintainer_email': __author__.split(' - ')[1],
    'author': __author__.split(' - ')[0],
    'author_email': __author__.split(' - ')[1],
    'url': 'https://github.com/nap/plexcleaner',
    'download_url': "https://github.com/nap/plexcleaner/archive/v{0}.zip".format(__version__),
    'license': 'http://www.apache.org/licenses/',
    'description': 'PlexCleaner will read your Plex Database and create a new library with '
                   'updated filename and directory structure including movie jacket of matched media.',
    'platforms': ['Linux'],
    'keywords': 'plex library movie media matching taglib jacket',
    'packages': find_packages(),
    'long_description': read('README.rst'),
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities',
    ]
}
setup(**setup_info)
