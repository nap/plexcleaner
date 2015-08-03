# PlexCleaner
This application will read the content of a Media Library and will generate a new media library, composed of the same 
files, renamed with the value Plex has stored, if necessary, with suggested format and directory structure.
This application rely on the working SQLITE3 database of the Plex Media Server to fetch information about files 
contained in the media library folder folder. If a file has the default value, this means it was not correctly 
matched by Plex therefore, this application will not transfer the media file to the new library.

## Suggested Media Library Format

```
. $NEW_LIBRARY/Movies
|- /Avatar (2009)
|  |- Avatar (2009).mkv
|  `- poster.jpg
`- /Batman Begins (2005)
   |- Batman Begins (2005).mp4
   |- Batman Begins (2005).eng.srt
   `- poster.jpg
```
