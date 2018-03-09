#!/usr/bin/python
# coding: utf-8

"""
prismedia_upload - tool to upload videos to Peertube and Youtube

Usage:
  prismedia_upload.py --file=<FILE> [options]
  prismedia_upload.py -h | --help
  prismedia_upload.py --version

Options:
  --name=NAME  Name of the video to upload. default to video file name
  -d, --description=STRING  Description of the video.
  -t, --tags=STRING  Tags for the video. comma separated
  -c, --category=STRING  Category for the videos, see below. Default to films
  --cca  License should be CreativeCommon Attribution (affects Youtube upload only)
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
"""
from os.path import dirname, realpath
import sys

from docopt import docopt


# Allows you to a relative import from the parent folder
sys.path.insert(0, dirname(realpath(__file__)) + "/lib")

import yt_upload
import pt_upload

try:
    from schema import Schema, And, Or, Optional, SchemaError
except ImportError:
    exit('This program requires that the `schema` data-validation library'
         ' is installed: \n'
         'see https://github.com/halst/schema\n')
try:
    import magic
except ImportError:
    exit('This program requires that the `magic` library'
         ' is installed, NOT the Python bindings to libmagic API \n'
         'see https://github.com/ahupp/python-magic\n')

VERSION = "prismedia 0.2-alpha"
VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')
VALID_CATEGORIES = (
    "music", "films", "vehicles",
    "sports", "travels", "gaming", "people",
    "comedy", "entertainment", "news",
    "how to", "education", "activism", "science & technology",
    "science", "technology", "animals"
    )


def validateVideo(path):
    supported_types = ['video/mp4']
    if magic.from_file(path, mime=True) in supported_types:
        return path
    else:
        return False

def validateCategory(category):
    if category.lower() in VALID_CATEGORIES:
        return True
    else:
        return False

if __name__ == '__main__':

    options = docopt(__doc__, version=VERSION)

    schema = Schema({
        '--file': And(str, validateVideo, error='file is not supported, please use mp4'),
        Optional('--name'): Or(None, And(str, lambda x: not x.isdigit(), error="The video name should be a string")),
        Optional('--description'): Or(None, And(str, lambda x: not x.isdigit(), error="The video name should be a string")),
        Optional('--tags'): Or(None, And(str, lambda x: not x.isdigit(), error="Tags should be a string")),
        Optional('--category'): Or(None, And(str, validateCategory, error="Category not recognized, please see --help")),
        Optional('--cca'): bool,
        '--help': bool,
        '--version': bool
    })

    try:
        options = schema.validate(options)
    except SchemaError as e:
        exit(e)

    yt_upload.run(options)
    pt_upload.run(options)
