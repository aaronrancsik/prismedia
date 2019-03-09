# Changelog

## v0.6.1-1 Hotfix
This fix prepares the python3 compatibility

 - Remove mastodon tags (mt) options as it's deprecated. Compatibility between Peertube and Mastodon is complete.

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