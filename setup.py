__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'
from setuptools import setup, find_packages

setup_info = {
    'name': 'plexcleaner',
    'version': '0.1.0',
    'maintainer': __author__.split(' - ')[0],
    'maintainer_email': __author__.split(' - ')[1],
    'author': __author__.split(' - ')[0],
    'author_email': __author__.split(' - ')[1],
    'url': 'http://{0}'.format(__author__.split('@')[1]),
    'license': 'http://www.apache.org/licenses/',
    'packages': find_packages(),
    'classifiers': [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia :: Video',
        'Topic :: Utilities',
    ],
    'entry_points': {
        'console_scripts': ['plexcleaner=plexcleaner:main']
    }
}
setup(**setup_info)
