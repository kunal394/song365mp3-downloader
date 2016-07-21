[![MIT Licence](https://badges.frapsoft.com/os/mit/mit-175x39.png?v=103)](https://opensource.org/licenses/mit-license.php)
[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source-175x29.png?v=103)](https://github.com/ellerbrock/open-source-badge/)

# song365mp3-downloader
song365mp3 music downloader in python

## Instructions

### Permission to execute the file
`chmod +x 365dn.py`

### Usage
```bash 
./365dn.py -h
usage: 365dn.py [-h] [-v] [-n] [-a] music_url

positional arguments:
  music_url        song365mp3 URL

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbose    increase output verbosity
  -n, --noconfirm  do not ask for confirmation
  -a, --all        download everything
```

### Example
`./365dn.py https://www.song365mp3.info/album/randartist-randalbum-12345.html` will create a folder named `Rand Album` and
download all the songs of that album, present on the song365mp3 url provided, in that folder and this folder will be inside a 
folder named `Rand Artist` (if that is the artist name provide on the artist's page). The artist's folder will be present inside
the current folder.

## Features

> Download a complete album given the url (`https://www.song365mp3.info/album/randartist-randalbum-12345.html`)

## TODO

> Download all songs of an artist given the url

> Download a single track given the url

> Implement regex input or a better way to help user select songs from the list instead of providing comma separated list.
