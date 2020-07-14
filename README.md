# Prismedia

Scripting your way to upload videos to peertube and youtube. Works with Python 3.5+.

[TOC]: #

## Table of Contents
- [Installation](#installation-and-upgrade)
  - [From pip](#from-pip)
  - [From source](#from-source)
- [Configuration](#configuration)
  - [Peertube](#peertube)
  - [Youtube](#youtube)
- [Usage](#usage)
- [Enhanced use of NFO](#enhanced-use-of-nfo)
- [Strict check options](#strict-check-options)
- [Features](#features)
- [Compatibility](#compatibility)
- [Inspirations](#inspirations)
- [Contributors](#contributors)

## Installation and upgrade

### From pip

Simply install with 

```bash
pip install prismedia
```

Upgrade with 

```bash
pip install --upgrade prismedia
```

### From source

Get the source: 

```bash
git clone https://git.lecygnenoir.info/LecygneNoir/prismedia.git prismedia
```

You may use pip to install requirements: `pip install -r requirements.txt` if you want to use the script directly.  
(*note:* requirements are generated via `poetry export -f requirements.txt`)

Otherwise, you can use [poetry](https://python-poetry.org), which create a virtualenv for the project directly  
(Or use the existing virtualenv if one is activated)

```
poetry install
```


## Configuration

Generate sample files with `python -m prismedia.genconfig`.  
Then rename and edit `peertube_secret` and `youtube_secret.json` with your credentials. (see below)

### Peertube
Set your credentials, peertube server URL.  
You can get client_id and client_secret by logging in your peertube website and reaching the URL:  
https://domain.example/api/v1/oauth-clients/local  
You can set ``OAUTHLIB_INSECURE_TRANSPORT`` to 1 if you do not use https (not recommended)

### Youtube
Youtube uses combination of oauth and API access to identify.

**Credentials**
The first time you connect, prismedia will open your browser to ask you to authenticate to
Youtube and allow the app to use your Youtube channel.  
**It is here you choose which channel you will upload to**.  
Once authenticated, the token is stored inside the file ``.youtube_credentials.json``.  
Prismedia will try to use this file at each launch, and re-ask for authentication if it does not exist.

**Oauth**:  
The default youtube_secret.json should allow you to upload some videos.  
If you plan a larger usage, please consider creating your own youtube_secret file:

 - Go to the [Google console](https://console.developers.google.com/).
 - Create project.
 - Side menu: APIs & auth -> APIs
 - Top menu: Enabled API(s): Enable all Youtube APIs.
 - Side menu: APIs & auth -> Credentials.
 - Create a Client ID: Add credentials -> OAuth 2.0 Client ID -> Other -> Name: prismedia1 -> Create -> OK
 - Download JSON: Under the section "OAuth 2.0 client IDs". Save the file to your local system.
 - Save this JSON as your youtube_secret.json file.

## Usage
Support only mp4 for cross compatibility between Youtube and Peertube.  
**Note that all options may be specified in a NFO file!** (see [Enhanced NFO](#enhanced-use-of-nfo))

Upload a video:

```
prismedia --file="yourvideo.mp4"
```

Specify description and tags:

```
prismedia --file="yourvideo.mp4" -d "My supa description" -t "tag1,tag2,foo"
```

Provide a thumbnail:

```
prismedia --file="yourvideo.mp4" -d "Video with thumbnail" --thumbnail="/path/to/your/thumbnail.jpg"
```


Use a NFO file to specify your video options:  
(See [Enhanced NFO](#enhanced-use-of-nfo) for more precise example)
```
prismedia --file="yourvideo.mp4" --nfo /path/to/your/nfo.txt
```


Use --help to get all available options:

```
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

## Enhanced use of NFO
Since Prismedia v0.9.0, the NFO system has been improved to allow hierarchical loading.
First of all, **if you already used nfo**, either with `--nfo` or by using `videoname.txt`, nothing changes :-)

But you are now able to use a more flexible NFO system, by using priorities. This allow you to set some defaults to avoid recreating a full nfo for each video

Basically, Prismedia will now load options in this order, using the last value found in case of conflict:  
`nfo.txt < directory_name.txt < video_name.txt < command line NFO < command line argument`

You'll find a complete set of samples in the [prismedia/samples](prismedia/samples) directory so let's take it as an example:
```
$ tree Recipes/
Recipes/
├── cli_nfo.txt
├── nfo.txt
├── samples.txt
├── yourvideo1.mp4
├── yourvideo1.txt
├── yourvideo1.jpg
├── yourvideo2.mp4
└── yourvideo2.txt
```

By using 
```
prismedia --file=/path/to/Recipes/yourvideo1.mp4 --nfo=/path/to/Recipes/cli_nfo.txt --cca
```

Prismedia will:
- look for options in `nfo.txt`
- look for options in `samples.txt` (from directory name) and erase any previous conflicting options
- look for options in `yourvideo1.txt` (from video name) and erase any previous conflicting options
- look for options in `cli_nfo.txt` (from the `--nfo` in command line) and erase any previous conflicting options
- erase any previous option regarding CCA as it's specified in cli with `--cca`
- take `yourvideo1.jpg` as thumbnail if no other files has been specified in previous NFO

In other word, Prismedia will now use option given in cli, then look for option in cli_nfo.txt, then complete with video_name.txt, then directory_name.txt, and finally complete with nfo.txt

It allows to specify more easily default options for an entire set of video, directory, playlist and so on.

## Strict check options
Since prismedia v0.10.0, a bunch of special options have been added to force the presence of parameters before uploading.
Strict options allow you to force some option to be present when uploading a video. It's useful to be sure you do not
forget something when uploading a video, for example if you use multiples NFO. You may force the presence of description,
tags, thumbnail, ...
All strict option are optionals and are provided only to avoid errors when uploading :-)
All strict options can be specified in NFO directly, the only strict option mandatory on cli is --withNFO
All strict options are off by default.

Available strict options:
  - --withNFO         Prevent the upload without a NFO, either specified via cli or found in the directory
  - --withThumbnail       Prevent the upload without a thumbnail
  - --withName        Prevent the upload if no name are found
  - --withDescription     Prevent the upload without description
  - --withTags        Prevent the upload without tags
  - --withPlaylist    Prevent the upload if no playlist
  - --withPublishAt    Prevent the upload if no schedule
  - --withPlatform    Prevent the upload if at least one platform is not specified
  - --withCategory    Prevent the upload if no category
  - --withLanguage    Prevent upload if no language
  - --withChannel     Prevent upload if no channel 

## Features

- [x] Youtube upload
- [x] Peertube upload
- Support of videos parameters (description, tags, category, licence, ...)
  - [x] description
  - [x] tags (no more than 30 characters per tag as Peertube does not support it)
  - [x] categories
  - [x] license: cca or not (Youtube only as Peertube uses Attribution by design)
  - [x] privacy (between public, unlisted or private)
  - [x] enabling/disabling comment (Peertube only as Youtube API does not support it)
  - [x] nsfw (Peertube only as Youtube API does not support it)
  - [x] set default language
  - [x] thumbnail
  - [x] multiple lines description (see [issue 4](https://git.lecygnenoir.info/LecygneNoir/prismedia/issues/4))
  - [x] add videos to playlist
  - [x] create playlist
  - [x] schedule your video with publishAt
  - [x] combine channel and playlist (Peertube only as channel is Peertube feature). See [issue 40](https://git.lecygnenoir.info/LecygneNoir/prismedia/issues/40) for detailed usage.
- [x] Use a config file (NFO) file to retrieve videos arguments
- [x] Allow choosing peertube or youtube upload (to retry a failed upload for example)
- [x] Usable on Desktop (Linux and/or Windows and/or MacOS)
- [x] Different schedules on platforms to prepare preview
- [x] Possibility to force the presence of upload options
- [ ] Copy and forget, eg possibility to copy video in a directory, and prismedia uploads itself (Discussions in [issue 27](https://git.lecygnenoir.info/LecygneNoir/prismedia/issues/27))  
- [ ] A usable graphical interface

## Compatibility

 - If you still use python2, use the version 0.7.1 (no more updated)
 - If you use peertube before 1.0.0-beta4, use the version inside tag 1.0.0-beta3

## Inspirations
Inspired by [peeror](https://git.rigelk.eu/rigelk/peeror) and [youtube-upload](https://github.com/tokland/youtube-upload)

## Contributors
Thanks to: @Zykino, @meewan, @rigelk 😘