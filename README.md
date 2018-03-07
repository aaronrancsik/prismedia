# ptyt_upload

A scripting way to upload videos to peertube and youtube

## Dependencies
Search in your package manager, otherwise use ``pip install --upgrade``
 - google-auth
 - google-auth-oauthlib
 - google-auth-httplib2
 - google-api-python-client
 - docopt
 - schema
 - magic
 - requests-toolbelt

## How To
Currently in heavy development

Support only mp4 for cross compatibily between Youtube and Peertube

```
./ptyt_upload.py --help
ptyt_upload - tool to upload videos to Peertube and Youtube

Usage: 
  ptyt_upload.py --file=<FILE> [options]
  ptyt_upload.py -h | --help
  ptyt_upload.py --version

Options:
  --name=NAME  Name of the video to upload. default to video file name
  -d, --description=STRING  Description of the video.
  -t, --tags=STRING  Tags for the video. comma separated
  -h --help  Show this help.
  --version  Show version.
```

## Features

- [X] Youtube upload
- [ ] Peertube upload
- [ ] Support of all videos arguments (description, tags, category, licence, ...)
- [ ] Use file to retrieve videos arguments
- [ ] Record and forget: put the video in a directory, and the script uploads it for you
- [ ] Usable on Desktop (Linux and/or Windows and/or MacOS)
- [ ] Graphical User Interface

## Sources 
inspired by [peeror](https://git.drycat.fr/rigelk/Peeror) and [youtube-upload](https://github.com/tokland/youtube-upload)