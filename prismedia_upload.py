#!/usr/bin/python
# coding: utf-8

"""
prismedia_upload - tool to upload videos to Peertube and Youtube

Usage:
  prismedia_upload.py --file=<FILE> [options]
  prismedia_upload.py --file=<FILE> --tags=STRING [--mt options]
  prismedia_upload.py -h | --help
  prismedia_upload.py --version

Options:
  --name=NAME  Name of the video to upload. (default to video filename)
  -d, --description=STRING  Description of the video. (default: default description)
  -t, --tags=STRING  Tags for the video. comma separated.
                     WARN: tags with space and special characters (!, ', ", ?, ...)
                           are not supported by Mastodon to be published from Peertube
                           use mastodon compatibility below
  --mt  Force Mastodon compatibility for tags (drop every incompatible characters inside tags)
        This option requires --tags
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
  --language=STRING  Specify the default language for video. See below for supported language. (default is English)
  --publishAt=DATE  Publish the video at the given DATE using local server timezone.
                    DATE should be on the form YYYY-MM-DDThh:mm:ss eg: 2018-03-12T19:00:00
                    DATE should be in the future
                    For Peertube, requires the "atd" and "curl utilities installed on the system
  --playlist=STRING Set the playlist to use for the video. Also known as Channel for Peertube.
                    If the playlist is not found, spawn an error except if --playlist-create is set.
  --playlistCreate  Create the playlist if not exists. (default do not create)
                    Only relevant if --playlist is set.
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

Languages:
  Language of the video (audio track), choose one. Default is English
  Here are available languages from Peertube and Youtube:
    Arabic, English, French, German, Hindi, Italian,
    Japanese, Korean, Mandarin, Portuguese, Punjabi, Russian, Spanish

"""
from os.path import dirname, realpath
import sys
import datetime
import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

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
    logging.error('This program requires that the `schema` data-validation library'
                  ' is installed: \n'
                  'see https://github.com/halst/schema\n')
    exit(1)
try:
    # noinspection PyUnresolvedReferences
    import magic
except ImportError:
    logging.error('This program requires that the `python-magic` library'
                  ' is installed, NOT the Python bindings to libmagic API \n'
                  'see https://github.com/ahupp/python-magic\n')
    exit(1)

VERSION = "prismedia v0.5"

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')
VALID_CATEGORIES = (
    "music", "films", "vehicles",
    "sports", "travels", "gaming", "people",
    "comedy", "entertainment", "news",
    "how to", "education", "activism", "science & technology",
    "science", "technology", "animals"
)
VALID_PLATFORM = ('youtube', 'peertube')
VALID_LANGUAGES = ('arabic', 'english', 'french',
                   'german', 'hindi', 'italian',
                   'japanese', 'korean', 'mandarin',
                   'portuguese', 'punjabi', 'russian', 'spanish')


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
        if plfrm.lower().replace(" ", "") not in VALID_PLATFORM:
            return False

    return True


def validateLanguage(language):
    if language.lower() in VALID_LANGUAGES:
        return True
    else:
        return False


def validatePublish(publish):
    # Check date format and if date is future
    try:
        now = datetime.datetime.now()
        publishAt = datetime.datetime.strptime(publish, '%Y-%m-%dT%H:%M:%S')
        if now >= publishAt:
            return False
    except ValueError:
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
        Optional('--mt'): bool,
        Optional('--category'): Or(None, And(
                                    str,
                                    validateCategory,
                                    error="Category not recognized, please see --help")
                                   ),
        Optional('--language'): Or(None, And(
                                    str,
                                    validateLanguage,
                                    error="Language not recognized, please see --help")
                                   ),
        Optional('--privacy'): Or(None, And(
                                    str,
                                    validatePrivacy,
                                    error="Please use recognized privacy between public, unlisted or private")
                                  ),
        Optional('--nfo'): Or(None, str),
        Optional('--platform'): Or(None, And(str, validatePlatform, error="Sorry, upload platform not supported")),
        Optional('--publishAt'): Or(None, And(
                                    str,
                                    validatePublish,
                                    error="DATE should be the form YYYY-MM-DDThh:mm:ss and has to be in the future")
                                    ),
        Optional('--cca'): bool,
        Optional('--disable-comments'): bool,
        Optional('--nsfw'): bool,
        Optional('--playlist'): Or(None, str),
        Optional('--playlistCreate'): bool,
        '--help': bool,
        '--version': bool
    })

    options = utils.parseNFO(options)

    try:
        options = schema.validate(options)
    except SchemaError as e:
        exit(e)

    if options.get('--platform') is None or "youtube" in options.get('--platform'):
        yt_upload.run(options)
    if options.get('--platform') is None or "peertube" in options.get('--platform'):
        pt_upload.run(options)
