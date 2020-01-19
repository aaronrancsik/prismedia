# Changelog

## vX.X.X

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