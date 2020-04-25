# Changelog

## v0.9.1

### Features
 - Possibility to bypass the MIME check for .mp4 when the user is sure of its video (#46 , thanks to @zykino)
 - Now **available with pip** for installation! (See the README for doc)


## v0.9.0

### Upgrade from v0.8.0
Now using [poetry](https://python-poetry.org/) for packaging and installing! It's easier to maintain and publish package, but means changes when using prismedia from command line.  

**Using poetry** (recommanded)

- [install poetry](https://python-poetry.org/docs/#installation)
- git pull the repo
- install prismedia:
```bash
poetry install
```
- use prismedia from the command line directly from your path:
```bash
prismedia -h
```

**From source**  
Prismedia is now seen as a python module, so you need to use `python -m prismedia` instead of `./prismedia_upload.py`.  
Once you have pulled the new v0.9.0, you may update by using:
```
pip install -r requirements.txt
# Then use prismedia through python command line:
python -m prismedia -h
```

### Features
 - Prismedia now uses [poetry](https://python-poetry.org) to allow easier installation usage and build, see the README (fix #34)
 - Add two new options to schedule video by platform. You may now use youtubeAt and peertubeAt to prepare previews (fix #43)
 - Enhance the NFO system to allow a hierarchical loading of multiple NFO, with priorities. See README and [prismedia/samples](prismedia/samples) for details (fix #11)

## v0.8.0

### Breaking changes
Now work with python 3! Support of python 2 is no longer available.  
You should now use python 3 in order to use prismedia

### Features
 - Add a requirements.txt file to make installing requirement easier.  
 - Add a debug option to show some infos before uploading (thanks to @zykino)  
 - Now uploading to Peertube before Youtube (thanks to @zykino)

## v0.7.1

### Fixes
Fix bug #42 , crash on Peertube when video has only one tag

## v0.7.0

### Features
Support Peertube channel additionally with playlist for Peertube!  
Peertube only as channel are Peertube's feature. See #40 for details.

### Fixes
 - Best uses of special chars in videoname, channel name and playlist name
 - Some fixes in logging message for better lisibility
 - Readme features list improved for better lisibility

## v0.6.4

### Fixes
 - Fix #33, no more trying to add a video into a playlist when the playlist does not exist on Youtube
 - fix #39, patch the playlist name check when playlist contains special chars

## v0.6.3

### Fixes
Fix Critical bug #38 that prevent upload when creating playlists on Peertube, as public playlist need a non-null channel_id.

## v0.6.2

**Warning**: your Peertube instance should be at least in v1.3.0 to use this new functionality.

### Features
New feature, the Peertube playlists are now supported!
We do not use channel in place of playlist anymore.

## v0.6.1-1 Hotfix
This fix prepares the python3 compatibility.  
**Warning** you need a new prerequisites: python-unidecode

 - Remove mastodon tags (mt) options as it's deprecated. Compatibility between Peertube and Mastodon is complete.
 - Simplify python2 specific functions

## v0.6.1

### Fixes
 - fix an error when playlists on Peertube have same names but not same display names (issue #20)
 - fix an error where videos does not upload on Peertube when some characters are used in playlist(issue #19)

## v0.6

### Compatibility ###
**Beware**, the first launch of prismedia for youtube will reask for credentials, this is needed for playlists.

This release is fully compatible with Peertube v1.0.0!

### Features
 - Add the possibility to upload thumbnail.
 - Add the possibility to configure playlist. (thanks @zykino for Peertube part)
 - Use the API instead of external binaries for publishAt for both Peertube and Youtube. (thanks @zykino)
 - Use the console option to authenticate against youtube for easier use with ssh'ed servers
 - Add -f as an alias for --file for easier upload.

## v0.5

### Features
 - plan your Peertube videos! Stable release
 - Support for Peertube beta4
 - More examples in NFO
 - Better support for multilines descriptions

### Fixes
 - Display datetime for output
 - plan video only if upload is successful