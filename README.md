# Prismedia

A scripting way to upload videos to peertube and youtube

## Dependencies
Search in your package manager, otherwise use ``pip install --upgrade``
 - google-auth
 - google-auth-oauthlib
 - google-auth-httplib2
 - google-api-python-client
 - docopt
 - schema
 - python-magic
 - requests-toolbelt

## How To
Currently in heavy development

Support only mp4 for cross compatibily between Youtube and Peertube

```
./prismedia_upload.py -h
prismedia_upload - tool to upload videos to Peertube and Youtube

Usage:
  prismedia_upload.py --file=<FILE> [options]
  prismedia_upload.py -h | --help
  prismedia_upload.py --version

Options:
  --name=NAME  Name of the video to upload. [default: video filename]
  -d, --description=STRING  Description of the video. [default: default description]
  -t, --tags=STRING  Tags for the video. comma separated
  -c, --category=STRING  Category for the videos, see below. [ default: Films]
  --cca  License should be CreativeCommon Attribution (affects Youtube upload only)
  -p, --privacy=STRING Choose between public, unlisted or private. [default: private]
  --disable-comments  Disable comments (Peertube only) [default: comments are enabled]
  --nsfw  Set the video as No Safe For Work (Peertube only as YT API does not support) [default: video is safe]
  -h --help  Show this help.
  --version  Show version.

Categories:
  Category is the type of video you upload. Default is films.
  Here are available categories from Peertube and Youtube:
    music, films, vehicles,
    sports, travels, gaming, people,
    comedy, entertainment, news,
    how to, education, activism, science & technology,
    science, technology, animals
```

## Features

- [x] Youtube upload
- [x] Peertube upload
- Support of all videos arguments (description, tags, category, licence, ...)
  - [x] description
  - [x] tags
  - [x] categories
  - [x] license: cca or not (Youtube only as Peertube uses Attribution by design)
  - [x] privacy (between public, unlisted or private)
  - [x] enabling/disabling comment (Peertube only as Youtube API does not support it)
  - [x] nsfw (Peertube only as Youtube API does not support it)
  - [ ] thumbnail/preview
- [ ] Use a config file (NFO) file to retrieve videos arguments
- [ ] Record and forget: put the video in a directory, and the script uploads it for you
- [ ] Usable on Desktop (Linux and/or Windows and/or MacOS)
- [ ] Graphical User Interface

## Sources 
inspired by [peeror](https://git.drycat.fr/rigelk/Peeror) and [youtube-upload](https://github.com/tokland/youtube-upload)