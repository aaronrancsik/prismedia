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


Use a NFO file to specify your video options:

```
./prismedia_upload.py --file="yourvideo.mp4" --nfo /path/to/your/nfo.txt
```


Use --help to get all available options:

```
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
```

## Features

- [x] Youtube upload
- [x] Peertube upload
- Support of all videos arguments (description, tags, category, licence, ...)
  - [x] description
  - [x] tags (no more than 30 characters per tag as Peertube does not support it)
  - [x] categories
  - [x] license: cca or not (Youtube only as Peertube uses Attribution by design)
  - [x] privacy (between public, unlisted or private)
  - [x] enabling/disabling comment (Peertube only as Youtube API does not support it)
  - [x] nsfw (Peertube only as Youtube API does not support it)
  - [ ] set default language
  - ~~thumbnail/preview~~ Canceled, waiting for Youtube's API support  
- [x] Use a config file (NFO) file to retrieve videos arguments
- [x] Allow to choose peertube or youtube upload (to resume failed upload for example)
- [ ] Record and forget: put the video in a directory, and the script uploads it for you
- [ ] Usable on Desktop (Linux and/or Windows and/or MacOS)
- [ ] Graphical User Interface

## Sources 
inspired by [peeror](https://git.drycat.fr/rigelk/Peeror) and [youtube-upload](https://github.com/tokland/youtube-upload)