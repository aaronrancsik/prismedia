# Prismedia

A scripting way to upload videos to peertube and youtube written in python2

## Dependencies
Search in your package manager, otherwise use ``pip install --upgrade``
 - google-auth
 - google-auth-oauthlib
 - google-auth-httplib2
 - google-api-python-client
 - docopt
 - schema
 - python-magic
 - python-magic-bin
 - requests-toolbelt
 - tzlocal

For Peertube and if you want to use the publishAt option, you also need some utilities on you local system
 - [atd](https://linux.die.net/man/8/atd) daemon
 - [curl](https://linux.die.net/man/1/curl)
 - [jq](https://stedolan.github.io/jq/)

## Configuration

Edit peertube_secret and youtube_secret.json with your credentials.

### Peertube
Set your credentials, peertube server URL.  
You can get client_id and client_secret by logging in your peertube website and reaching the URL: https://domain.example/api/v1/oauth-clients/local
You can set ``OAUTHLIB_INSECURE_TRANSPORT`` to 1 if you do not use https (not recommended)

### Youtube
Youtube uses combination of oauth and API access to identify.

**Credentials**
The first time you connect, prismedia will open your browser to as you to authenticate to
Youtube and allow the app to use your Youtube channel.  
**It is here you choose which channel you will upload to**.  
Once authenticated, the token is stored inside the file ``.youtube_credentials.json``.  
Prismedia will try to use this file at each launch, and re-ask for authentication if it does not exist.

**Oauth**:  
The default youtube_secret.json should allow you to upload some videos.  
If you plan an larger usage, please consider creating your own youtube_secret file:

- Go to the [Google console](https://console.developers.google.com/).
- Create project.
- Side menu: APIs & auth -> APIs
- Top menu: Enabled API(s): Enable all Youtube APIs.
- Side menu: APIs & auth -> Credentials.
- Create a Client ID: Add credentials -> OAuth 2.0 Client ID -> Other -> Name: prismedia1 -> Create -> OK
- Download JSON: Under the section "OAuth 2.0 client IDs". Save the file to your local system.
- Save this JSON as your youtube_secret.json file.

## How To
Currently in heavy development

Support only mp4 for cross compatibility between Youtube and Peertube

Simply upload a video:

```
./prismedia_upload.py --file="yourvideo.mp4"
```


Specify description and tags:

```
./prismedia_upload.py --file="yourvideo.mp4" -d "My supa description" -t "tag1,tag2,foo"
```

Provide a thumbnail:

```
./prismedia_upload.py --file="yourvideo.mp4" -d "Video with thumbnail" --thumbnail="/path/to/your/thumbnail.jpg"
```


Use a NFO file to specify your video options:

```
./prismedia_upload.py --file="yourvideo.mp4" --nfo /path/to/your/nfo.txt
```


Use --help to get all available options:

```
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
  --thumbnail=STRING    Path to a file to use as a thumbnail for the video.
                        Supported types are jpg and jpeg.
                        By default, prismedia search for an image based on video name followed by .jpg or .jpeg
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
```

## Features

- [x] Youtube upload
- [x] Peertube upload
- Support of all videos arguments (description, tags, category, licence, ...)
  - [x] description
  - [x] tags (no more than 30 characters per tag as Peertube does not support it)
  - [x] Option to force tags to be compatible with Mastodon publication
  - [x] categories
  - [x] license: cca or not (Youtube only as Peertube uses Attribution by design)
  - [x] privacy (between public, unlisted or private)
  - [x] enabling/disabling comment (Peertube only as Youtube API does not support it)
  - [x] nsfw (Peertube only as Youtube API does not support it)
  - [x] set default language
  - [x] thumbnail/preview
  - [x] multiple lines description (see [issue 4](https://git.lecygnenoir.info/LecygneNoir/prismedia/issues/4))
  - [x] add videos to playlist for Peertube
  - [ ] add videos to playlist for Youtube
- [x] Use a config file (NFO) file to retrieve videos arguments
- [x] Allow to choose peertube or youtube upload (to resume failed upload for example)
- [x] Add publishAt option to plan your videos (need the [atd](https://linux.die.net/man/8/atd) daemon, [curl](https://linux.die.net/man/1/curl) and [jq](https://stedolan.github.io/jq/))
- [ ] Record and forget: put the video in a directory, and the script uploads it for you
- [ ] Usable on Desktop (Linux and/or Windows and/or MacOS)
- [ ] Graphical User Interface

## Compatibility

If your server uses peertube before 1.0.0-beta4, use the version inside tag 1.0.0-beta3!

## Sources
inspired by [peeror](https://git.rigelk.eu/rigelk/peeror) and [youtube-upload](https://github.com/tokland/youtube-upload)