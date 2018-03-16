#!/usr/bin/python
# coding: utf-8

"""
prismedia_upload - tool to upload videos to Peertube and Youtube

Usage:
  prismedia_upload.py --file=<FILE> [options]
  prismedia_upload.py -h | --help
  prismedia_upload.py --version

Options:
  --name=NAME  Name of the video to upload. (default to video filename)
  -d, --description=STRING  Description of the video. (default: default description)
  -t, --tags=STRING  Tags for the video. comma separated
  -c, --category=STRING  Category for the videos, see below. (default: Films)
  --cca  License should be CreativeCommon Attribution (affects Youtube upload only)
  -p, --privacy=STRING  Choose between public, unlisted or private. (default: private)
  --disable-comments  Disable comments (Peertube only as YT API does not support) (default: comments are enabled)
  --nsfw  Set the video as No Safe For Work (Peertube only as YT API does not support) (default: video is safe)
  --nfo=STRING  Configure a specific nfo file to set options for the video.
                By default Prismedia search a .txt based on video name
                See nfo_example.txt for more details
  --platform=STRING  List of platform(s) to upload to, comma separated.
                     Supported platforms are youtube and peertube (default is both)
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


# Allows a relative import from the parent folder
sys.path.insert(0, dirname(realpath(__file__)) + "/lib")

import yt_upload
import pt_upload
import utils

try:
    # noinspection PyUnresolvedReferences
    from schema import Schema, And, Or, Optional, SchemaError
except ImportError:
    exit('This program requires that the `schema` data-validation library'
         ' is installed: \n'
         'see https://github.com/halst/schema\n')
try:
    # noinspection PyUnresolvedReferences
    import magic
except ImportError:
    exit('This program requires that the `python-magic` library'
         ' is installed, NOT the Python bindings to libmagic API \n'
         'see https://github.com/ahupp/python-magic\n')

VERSION = "prismedia 0.3"
VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')
VALID_CATEGORIES = (
    "music", "films", "vehicles",
    "sports", "travels", "gaming", "people",
    "comedy", "entertainment", "news",
    "how to", "education", "activism", "science & technology",
    "science", "technology", "animals"
)
VALID_PLATFORM = ('youtube', 'peertube')


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


def validatePrivacy(privacy):
    if privacy.lower() in VALID_PRIVACY_STATUSES:
        return True
    else:
        return False


def validatePlatform(platform):
    for plfrm in platform.split(','):
        if plfrm not in VALID_PLATFORM:
            return False

    return True


if __name__ == '__main__':

    options = docopt(__doc__, version=VERSION)

    schema = Schema({
        '--file': And(str, validateVideo, error='file is not supported, please use mp4'),
        Optional('--name'): Or(None, And(
                                str,
                                lambda x: not x.isdigit(),
                                error="The video name should be a string")
                               ),
        Optional('--description'): Or(None, And(
                                        str,
                                        lambda x: not x.isdigit(),
                                        error="The video name should be a string")
                                      ),
        Optional('--tags'): Or(None, And(
                                    str,
                                    lambda x: not x.isdigit(),
                                    error="Tags should be a string")
                               ),
        Optional('--category'): Or(None, And(
                                    str,
                                    validateCategory,
                                    error="Category not recognized, please see --help")
                                   ),
        Optional('--privacy'): Or(None, And(
                                    str,
                                    validatePrivacy,
                                    error="Please use recognized privacy between public, unlisted or private")
                                  ),
        Optional('--nfo'): Or(None, str),
        Optional('--platform'): Or(None, And(str, validatePlatform, error="Sorry, upload platform not supported")),
        Optional('--cca'): bool,
        Optional('--disable-comments'): bool,
        Optional('--nsfw'): bool,
        '--help': bool,
        '--version': bool
    })

    try:
        options = schema.validate(options)
    except SchemaError as e:
        exit(e)

    options = utils.parseNFO(options)

    if options.get('--platform') is None or "youtube" in options.get('--platform'):
        yt_upload.run(options)
    if options.get('--platform') is None or "peertube" in options.get('--platform'):
        pt_upload.run(options)
