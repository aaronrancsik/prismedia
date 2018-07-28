#!/usr/bin/python
# coding: utf-8

from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from os.path import dirname, splitext, basename, isfile
from os import devnull
from subprocess import check_call, CalledProcessError, STDOUT
import unicodedata
import logging

### CATEGORIES ###
YOUTUBE_CATEGORY = {
    "music": 10,
    "films": 1,
    "vehicles": 2,
    "sport": 17,
    "travels": 19,
    "gaming": 20,
    "people": 22,
    "comedy": 23,
    "entertainment": 24,
    "news": 25,
    "how to": 26,
    "education": 27,
    "activism": 29,
    "science & technology": 28,
    "science": 28,
    "technology": 28,
    "animals": 15
}

PEERTUBE_CATEGORY = {
    "music": 1,
    "films": 2,
    "vehicles": 3,
    "sport": 5,
    "travels": 6,
    "gaming": 7,
    "people": 8,
    "comedy": 9,
    "entertainment": 10,
    "news": 11,
    "how to": 12,
    "education": 13,
    "activism": 14,
    "science & technology": 15,
    "science": 15,
    "technology": 15,
    "animals": 16
}

### LANGUAGES ###
YOUTUBE_LANGUAGE = {
    "arabic": 'ar',
    "english": 'en',
    "french": 'fr',
    "german": 'de',
    "hindi": 'hi',
    "italian": 'it',
    "japanese": 'ja',
    "korean": 'ko',
    "mandarin": 'zh-CN',
    "portuguese": 'pt-PT',
    "punjabi": 'pa',
    "russian": 'ru',
    "spanish": 'es'
}

PEERTUBE_LANGUAGE = {
    "arabic": "ar",
    "english": "en",
    "french": "fr",
    "german": "de",
    "hindi": "hi",
    "italian": "it",
    "japanese": "ja",
    "korean": "ko",
    "mandarin": "zh",
    "portuguese": "pt",
    "punjabi": "pa",
    "russian": "ru",
    "spanish": "es"
}
######################


def getCategory(category, platform):
    if platform == "youtube":
        return YOUTUBE_CATEGORY[category.lower()]
    else:
        return PEERTUBE_CATEGORY[category.lower()]


def getLanguage(language, platform):
    if platform == "youtube":
        return YOUTUBE_LANGUAGE[language.lower()]
    else:
        return PEERTUBE_LANGUAGE[language.lower()]


def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if value:
                good_kwargs[key] = value
    return good_kwargs

def searchThumbnail(options):
    video_directory = dirname(options.get('--file')) + "/"
    # First, check for thumbnail based on videoname
    if options.get('--name'):
        if isfile(video_directory + options.get('--name') + ".jpg"):
            options['--thumbnail'] = video_directory + options.get('--name') + ".jpg"
        elif isfile(video_directory + options.get('--name') + ".jpeg"):
            options['--thumbnail'] = video_directory + options.get('--name') + ".jpeg"
    # Then, if we still not have thumbnail, check for thumbnail based on videofile name
    if not options.get('--thumbnail'):
        video_file = splitext(basename(options.get('--file')))[0]
        if isfile(video_directory + video_file + ".jpg"):
            options['--thumbnail'] = video_directory + video_file + ".jpg"
        elif isfile(video_directory + video_file + ".jpeg"):
            options['--thumbnail'] = video_directory + video_file + ".jpeg"
    return options


# return the nfo as a RawConfigParser object
def loadNFO(options):
    video_directory = dirname(options.get('--file')) + "/"
    if options.get('--nfo'):
        try:
            logging.info("Using " + options.get('--nfo') + " as NFO, loading...")
            if isfile(options.get('--nfo')):
                nfo = RawConfigParser()
                nfo.read(options.get('--nfo'))
                return nfo
            else:
                logging.error("Given NFO file does not exist, please check your path.")
                exit(1)
        except Exception as e:
            logging.error("Problem with NFO file: " + str(e))
            exit(1)
    else:
        if options.get('--name'):
            nfo_file = video_directory + options.get('--name') + ".txt"
            if isfile(nfo_file):
                try:
                    logging.info("Using " + nfo_file + " as NFO, loading...")
                    nfo = RawConfigParser()
                    nfo.read(nfo_file)
                    return nfo
                except Exception as e:
                    logging.error("Problem with NFO file: " + str(e))
                    exit(1)

    # if --nfo and --name does not exist, use --file as default
    video_file = splitext(basename(options.get('--file')))[0]
    nfo_file = video_directory + video_file + ".txt"
    if isfile(nfo_file):
        try:
            logging.info("Using " + nfo_file + " as NFO, loading...")
            nfo = RawConfigParser()
            nfo.read(nfo_file)
            return nfo
        except Exception as e:
            logging.error("Problem with nfo file: " + str(e))
            exit(1)
    logging.info("No suitable NFO found, skipping.")
    return False


def parseNFO(options):
    nfo = loadNFO(options)
    if nfo:
        # We need to check all options and replace it with the nfo value if not defined (None or False)
        for key, value in options.iteritems():
            key = key.replace("-", "")
            try:
                # get string options
                if value is None and nfo.get('video', key):
                    options['--' + key] = nfo.get('video', key)
                # get boolean options
                elif value is False and nfo.getboolean('video', key):
                    options['--' + key] = nfo.getboolean('video', key)
            except NoOptionError:
                continue
            except NoSectionError:
                logging.error("Given NFO file miss section [video], please check syntax of your NFO.")
                exit(1)
    return options


def upcaseFirstLetter(s):
    return s[0].upper() + s[1:]


def publishAt(publishAt, oauth, url, idvideo, secret):
    try:
        FNULL = open(devnull, 'w')
        check_call(["at", "-V"], stdout=FNULL, stderr=STDOUT)
    except CalledProcessError:
        logging.error("You need to install the atd daemon to use the publishAt option.")
        exit(1)
    try:
        FNULL = open(devnull, 'w')
        check_call(["curl", "-V"], stdout=FNULL, stderr=STDOUT)
    except CalledProcessError:
        logging.error("You need to install the curl command line to use the publishAt option.")
        exit(1)
    try:
        FNULL = open(devnull, 'w')
        check_call(["jq", "-V"], stdout=FNULL, stderr=STDOUT)
    except CalledProcessError:
        logging.error("You need to install the jq command line to use the publishAt option.")
        exit(1)
    time = publishAt.split("T")
    # Remove leading seconds that atd does not manage
    if time[1].count(":") == 2:
        time[1] = time[1][:-3]

    atTime = time[1] + " " + time[0]
    refresh_token=str(oauth.__dict__['_client'].__dict__['refresh_token'])
    atFile = "/tmp/peertube_" + idvideo + "_" + publishAt + ".at"
    try:
        openfile = open(atFile,"w")
        openfile.write('token=$(curl -X POST -d "client_id=' + str(secret.get('peertube', 'client_id')) +
                        '&client_secret=' + str(secret.get('peertube', 'client_secret')) +
                        '&grant_type=refresh_token&refresh_token=' + str(refresh_token) +
                        '" "' + url + '/api/v1/users/token" | jq -r .access_token)')
        openfile.write("\n")
        openfile.write('curl "' + url + '/api/v1/videos/' + idvideo +
                        '" -X PUT -H "Authorization: Bearer ${token}"' +
                        ' -H "Content-Type: multipart/form-data" -F "privacy=1"')
        openfile.write("\n ")  # atd needs an empty line at the end of the file to load...
        openfile.close()
    except Exception as e:
        if hasattr(e, 'message'):
            logging.error("Error: " + str(e.message))
        else:
            logging.error("Error: " + str(e))

    try:
        FNULL = open(devnull, 'w')
        check_call(["at", "-M", "-f", atFile, atTime], stdout=FNULL, stderr=STDOUT)
    except Exception as e:
        if hasattr(e, 'message'):
            logging.error("Error: " + str(e.message))
        else:
            logging.error("Error: " + str(e))


def mastodonTag(tag):
    tags = tag.split(' ')
    mtag = ''
    for s in tags:
        if s == '':
            continue
        strtag = unicodedata.normalize('NFKD', unicode (s, 'utf-8')).encode('ASCII', 'ignore')
        strtag = ''.join(e for e in strtag if e.isalnum())
        strtag = upcaseFirstLetter(strtag)
        mtag = mtag + strtag

    return mtag
