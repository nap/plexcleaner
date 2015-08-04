PlexCleaner
===========

**Require python >= 2.7**

This application will read the content of a Media Library and will generate a new media library, composed of the same 
files, renamed with the value Plex has stored, if necessary, with suggested format and directory structure.
This application rely on the working SQLITE3 database of the Plex Media Server to fetch information about files 
contained in the media library folder folder. If a file has the default value, this means it was not correctly 
matched by Plex therefore, this application will not transfer the media file to the new library.

Example
-------
::

    unary$ python plexcleaner/cleaner.py --help
    Usage: cleaner.py [OPTIONS]
    
    Options:
      --plex-home PATH                Installation location of the Plex Media
                                      Server.
      --new-library PATH              Where to consolidate the updated library.
      --jacket TEXT                   Name that each movie jacket will have.
      --database-override PATH        Override the expected Plex Database
                                      location.
      --interrupt                     Interrupt the whole process if a movie file
                                      is not found.
      --log-level [DEBUG|INFO|WARNING|CRITICAL|ERROR]
                                      Application verbosity, default is INFO
      --move-media                    Should the tool move or copy to the new
                                      library.
      --help                          Show this message and exit.


Suggested Media Library Format
------------------------------
::

    . $NEW_LIBRARY/Movies
    |- /Avatar (2009)
    |  |- Avatar (2009).mkv
    |  `- poster.jpg
    `- /Batman Begins (2005)
       |- Batman Begins (2005).mp4
       |- Batman Begins (2005).eng.srt
       `- poster.jpg

:Version: 0.0.1 of 2015-XX-XX