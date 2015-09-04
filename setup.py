__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'
__version__ = '0.1a0'

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox  # import here, cause outside the eggs aren't loaded
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


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
    'tests_require': ['tox'],
    'cmdclass': {'test': Tox},
    'entry_points': {
        'console_scripts': ['plexcleaner = plexcleaner.cleaner:clean']
    },
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
