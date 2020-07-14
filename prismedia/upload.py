#!/usr/bin/env python
# coding: utf-8

"""
prismedia - tool to upload videos to Peertube and Youtube

Usage:
  prismedia --file=<FILE> [options]
  prismedia -f <FILE> --tags=STRING [options]
  prismedia -h | --help
  prismedia --version

Options:
  -f, --file=STRING Path to the video file to upload in mp4
  --name=NAME  Name of the video to upload. (default to video filename)
  --debug  Trigger some debug information like options used (default: no)
  -d, --description=STRING  Description of the video. (default: default description)
  -t, --tags=STRING  Tags for the video. comma separated.
                     WARN: tags with punctuation (!, ', ", ?, ...)
                           are not supported by Mastodon to be published from Peertube
  -c, --category=STRING  Category for the videos, see below. (default: Films)
  --cca  License should be CreativeCommon Attribution (affects Youtube upload only)
  -p, --privacy=STRING  Choose between public, unlisted or private. (default: private)
  --disable-comments  Disable comments (Peertube only as YT API does not support) (default: comments are enabled)
  --nsfw  Set the video as No Safe For Work (Peertube only as YT API does not support) (default: video is safe)
  --nfo=STRING  Configure a specific nfo file to set options for the video.
                By default Prismedia search a .txt based on the video name and will
                decode the file as UTF-8 (so make sure your nfo file is UTF-8 encoded)
                See nfo_example.txt for more details
  --platform=STRING  List of platform(s) to upload to, comma separated.
                     Supported platforms are youtube and peertube (default is both)
  --language=STRING  Specify the default language for video. See below for supported language. (default is English)
  --publishAt=DATE  Publish the video at the given DATE using local server timezone.
                    DATE should be on the form YYYY-MM-DDThh:mm:ss eg: 2018-03-12T19:00:00
                    DATE should be in the future
  --peertubeAt=DATE
  --youtubeAt=DATE  Override publishAt for the corresponding platform. Allow to create preview on specific platform
  --thumbnail=STRING    Path to a file to use as a thumbnail for the video.
                        Supported types are jpg and jpeg.
                        By default, prismedia search for an image based on video name followed by .jpg or .jpeg
  --channel=STRING Set the channel to use for the video (Peertube only)
                    If the channel is not found, spawn an error except if --channelCreate is set.
  --channelCreate  Create the channel if not exists. (Peertube only, default do not create)
                   Only relevant if --channel is set.
  --playlist=STRING Set the playlist to use for the video.
                    If the playlist is not found, spawn an error except if --playlistCreate is set.
  --playlistCreate  Create the playlist if not exists. (default do not create)
                    Only relevant if --playlist is set.
  -h --help  Show this help.
  --version  Show version.

Strict options:
  Strict options allow you to force some option to be present when uploading a video. It's useful to be sure you do not
  forget something when uploading a video, for example if you use multiples NFO. You may force the presence of description,
  tags, thumbnail, ...
  All strict option are optionals and are provided only to avoid errors when uploading :-)
  All strict options can be specified in NFO directly, the only strict option mandatory on cli is --withNFO
  All strict options are off by default

  --withNFO         Prevent the upload without a NFO, either specified via cli or found in the directory
  --withThumbnail       Prevent the upload without a thumbnail
  --withName        Prevent the upload if no name are found
  --withDescription     Prevent the upload without description
  --withTags        Prevent the upload without tags
  --withPlaylist    Prevent the upload if no playlist
  --withPublishAt    Prevent the upload if no schedule
  --withPlatform    Prevent the upload if at least one platform is not specified
  --withCategory    Prevent the upload if no category
  --withLanguage    Prevent upload if no language
  --withChannel     Prevent upload if no channel

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
import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import datetime
import logging
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

from docopt import docopt

from . import yt_upload
from . import pt_upload
from . import utils

try:
    # noinspection PyUnresolvedReferences
    from schema import Schema, And, Or, Optional, SchemaError, Hook
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

VERSION = "prismedia v0.9.1"

VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')
VALID_CATEGORIES = (
    "music", "films", "vehicles",
    "sports", "travels", "gaming", "people",
    "comedy", "entertainment", "news",
    "how to", "education", "activism", "science & technology",
    "science", "technology", "animals"
)
VALID_PLATFORM = ('youtube', 'peertube', 'none')
VALID_LANGUAGES = ('arabic', 'english', 'french',
                   'german', 'hindi', 'italian',
                   'japanese', 'korean', 'mandarin',
                   'portuguese', 'punjabi', 'russian', 'spanish')


def validateVideo(path):
    supported_types = ['video/mp4']
    detected_type = magic.from_file(path, mime=True)
    if detected_type not in supported_types:
        print("File", path, "detected type is", detected_type, "which is not one of", supported_types)

        force_file = ['y', 'yes']
        is_forcing = input("Are you sure you selected the correct file? (y/N)")
        if is_forcing.lower() not in force_file:
            return False

    return path


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


def validateThumbnail(thumbnail):
    supported_types = ['image/jpg', 'image/jpeg']
    if os.path.exists(thumbnail) and \
            magic.from_file(thumbnail, mime=True) in supported_types:
        return thumbnail
    else:
        return False


def _optionnalOrStrict(key, scope, error):
    option = key.replace('-', '')
    option = option[0].upper() + option[1:]
    if scope["--with" + option] is True and scope[key] is None:
        logging.error("Prismedia: you have required the strict presence of " + key + " but none is found")
        exit(1)
    return True


def main():
    options = docopt(__doc__, version=VERSION)

    strictoptionSchema = Schema({
        Optional('--withNFO', default=False): bool,
        Optional('--withThumbnail', default=False): bool,
        Optional('--withName', default=False): bool,
        Optional('--withDescription', default=False): bool,
        Optional('--withTags', default=False): bool,
        Optional('--withPlaylist', default=False): bool,
        Optional('--withPublishAt', default=False): bool,
        Optional('--withPlatform', default=False): bool,
        Optional('--withCategory', default=False): bool,
        Optional('--withLanguage', default=False): bool,
        Optional('--withChannel', default=False): bool,
        object: object # This allow to return all other options for further use: https://github.com/keleshev/schema#extra-keys
    })

    schema = Schema({
        '--file': And(str, os.path.exists, validateVideo, error='file is not supported, please use mp4'),
        # Strict option checks - at the moment Schema needs to check Hook and Optional separately #
        Hook('--name', handler=_optionnalOrStrict): object,
        Hook('--description', handler=_optionnalOrStrict): object,
        Hook('--tags', handler=_optionnalOrStrict): object,
        Hook('--category', handler=_optionnalOrStrict): object,
        Hook('--language', handler=_optionnalOrStrict): object,
        Hook('--platform', handler=_optionnalOrStrict): object,
        Hook('--publishAt', handler=_optionnalOrStrict): object,
        Hook('--thumbnail', handler=_optionnalOrStrict): object,
        Hook('--channel', handler=_optionnalOrStrict): object,
        Hook('--playlist', handler=_optionnalOrStrict): object,
        # Validate checks #
        Optional('--name'): Or(None, And(
                                str,
                                lambda x: not x.isdigit(),
                                error="The video name should be a string")
                               ),
        Optional('--description'): Or(None, And(
                                        str,
                                        lambda x: not x.isdigit(),
                                        error="The video description should be a string")
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
        Optional('--peertubeAt'): Or(None, And(
                                    str,
                                    validatePublish,
                                    error="DATE should be the form YYYY-MM-DDThh:mm:ss and has to be in the future")
                                    ),
        Optional('--youtubeAt'): Or(None, And(
                                    str,
                                    validatePublish,
                                    error="DATE should be the form YYYY-MM-DDThh:mm:ss and has to be in the future")
                                    ),
        Optional('--debug'): bool,
        Optional('--cca'): bool,
        Optional('--disable-comments'): bool,
        Optional('--nsfw'): bool,
        Optional('--thumbnail'): Or(None, And(
                                    str, validateThumbnail, error='thumbnail is not supported, please use jpg/jpeg'),
                                    ),
        Optional('--channel'): Or(None, str),
        Optional('--channelCreate'): bool,
        Optional('--playlist'): Or(None, str),
        Optional('--playlistCreate'): bool,
        '--help': bool,
        '--version': bool,
        object: object # This allow to return all other options for further use: https://github.com/keleshev/schema#extra-keys
    })

    # We need to validate strict options first as withNFO should be validated before NFO parsing
    try:
        options = strictoptionSchema.validate(options)
    except SchemaError as e:
        exit(e)

    options = utils.parseNFO(options)

    # Once NFO are loaded, we need to revalidate strict options in case some were in NFO
    try:
        options = strictoptionSchema.validate(options)
    except SchemaError as e:
        exit(e)

    if not options.get('--thumbnail'):
        options = utils.searchThumbnail(options)

    try:
        options = schema.validate(options)
    except SchemaError as e:
        exit(e)

    if options.get('--debug'):
        print("Python " + sys.version)
        print(options)

    if options.get('--platform') is None or "peertube" in options.get('--platform'):
        pt_upload.run(options)
    if options.get('--platform') is None or "youtube" in options.get('--platform'):
        yt_upload.run(options)


if __name__ == '__main__':
    import warnings
    warnings.warn("use 'python -m prismedia', not 'python -m prismedia.upload'", DeprecationWarning)
    main()
