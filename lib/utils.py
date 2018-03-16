#!/usr/bin/python
# coding: utf-8

from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from os.path import dirname, splitext, basename, isfile

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
    "arabic": 5,
    "english": 1,
    "french": 13,
    "german": 11,
    "hindi": 4,
    "italian": 14,
    "japanese": 9,
    "korean": 12,
    "mandarin": 3,
    "portuguese": 6,
    "punjabi": 10,
    "russian": 8,
    "spanish": 2
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


# return the nfo as a RawConfigParser object
def loadNFO(options):
    video_directory = dirname(options.get('--file')) + "/"
    if options.get('--nfo'):
        try:
            print "Using " + options.get('--nfo') + " as NFO, loading..."
            if isfile(options.get('--nfo')):
                nfo = RawConfigParser()
                nfo.read(options.get('--nfo'))
                return nfo
            else:
                exit("Given NFO file does not exist, please check your path.")
        except Exception as e:
            exit("Problem with NFO file: " + str(e))
    else:
        if options.get('--name'):
            nfo_file = video_directory + options.get('--name') + ".txt"
            print nfo_file
            if isfile(nfo_file):
                try:
                    print "Using " + nfo_file + " as NFO, loading..."
                    nfo = RawConfigParser()
                    nfo.read(nfo_file)
                    return nfo
                except Exception as e:
                    exit("Problem with NFO file: " + str(e))

    # if --nfo and --name does not exist, use --file as default
    video_file = splitext(basename(options.get('--file')))[0]
    nfo_file = video_directory + video_file + ".txt"
    if isfile(nfo_file):
        try:
            print "Using " + nfo_file + " as NFO, loading..."
            nfo = RawConfigParser()
            nfo.read(nfo_file)
            return nfo
        except Exception as e:
            exit("Problem with nfo file: " + str(e))
    print "No suitable NFO found, skipping."
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
                exit("Given NFO file miss section [video], please check syntax of your NFO.")
    return options
