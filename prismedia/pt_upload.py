#!/usr/bin/env python
# coding: utf-8

import os
import mimetypes
import json
import logging
import datetime
import pytz
from os.path import splitext, basename, abspath
from tzlocal import get_localzone

from configparser import RawConfigParser
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient
from requests_toolbelt.multipart.encoder import MultipartEncoder

from . import utils

PEERTUBE_SECRETS_FILE = 'peertube_secret'
PEERTUBE_PRIVACY = {
    "public": 1,
    "unlisted": 2,
    "private": 3
}


def get_authenticated_service(secret):
    peertube_url = str(secret.get('peertube', 'peertube_url')).rstrip("/")

    oauth_client = LegacyApplicationClient(
        client_id=str(secret.get('peertube', 'client_id'))
    )
    try:
        oauth = OAuth2Session(client=oauth_client)
        oauth.fetch_token(
            token_url=str(peertube_url + '/api/v1/users/token'),
            # lower as peertube does not store uppercase for pseudo
            username=str(secret.get('peertube', 'username').lower()),
            password=str(secret.get('peertube', 'password')),
            client_id=str(secret.get('peertube', 'client_id')),
            client_secret=str(secret.get('peertube', 'client_secret'))
        )
    except Exception as e:
        if hasattr(e, 'message'):
            logging.error("Peertube: Error: " + str(e.message))
            exit(1)
        else:
            logging.error("Peertube: Error: " + str(e))
            exit(1)
    return oauth


def get_default_channel(user_info):
    return user_info['videoChannels'][0]['id']


def get_channel_by_name(user_info, options):
    for channel in user_info["videoChannels"]:
        if channel['displayName'] == options.get('--channel'):
            return channel['id']


def create_channel(oauth, url, options):
    template = ('Peertube: Channel %s does not exist, creating it.')
    logging.info(template % (str(options.get('--channel'))))
    channel_name = utils.cleanString(str(options.get('--channel')))
    # Peertube allows 20 chars max for channel name
    channel_name = channel_name[:19]
    data = '{"name":"' + channel_name + '", \
            "displayName":"' + options.get('--channel') + '", \
            "description":null, \
            "support":null}'

    headers = {
        'Content-Type': "application/json; charset=UTF-8"
    }
    try:
        response = oauth.post(url + "/api/v1/video-channels/",
                              data=data.encode('utf-8'),
                              headers=headers)
    except Exception as e:
        if hasattr(e, 'message'):
            logging.error("Error: " + str(e.message))
        else:
            logging.error("Error: " + str(e))
    if response is not None:
        if response.status_code == 200:
            jresponse = response.json()
            jresponse = jresponse['videoChannel']
            return jresponse['id']
        if response.status_code == 409:
            logging.error('Peertube: Error: It seems there is a conflict with an existing channel named '
                          + channel_name + '.'
                          ' Please beware Peertube internal name is compiled from 20 firsts characters of channel name.'
                          ' Also note that channel name are not case sensitive (no uppercase nor accent)'
                          ' Please check your channel name and retry.')
            exit(1)
        else:
            logging.error(('Peertube: Creating channel failed with an unexpected response: '
                           '%s') % response)
            exit(1)


def get_default_playlist(user_info):
    return user_info['videoChannels'][0]['id']


def get_playlist_by_name(user_playlists, options):
    for playlist in user_playlists["data"]:
        if playlist['displayName'] == options.get('--playlist'):
            return playlist['id']


def create_playlist(oauth, url, options, channel):
    template = ('Peertube: Playlist %s does not exist, creating it.')
    logging.info(template % (str(options.get('--playlist'))))
    # We use files for form-data Content
    # see https://requests.readthedocs.io/en/latest/user/quickstart/#post-a-multipart-encoded-file
    # None is used to mute "filename" field
    files = {'displayName': (None, str(options.get('--playlist'))),
             'privacy': (None, "1"),
             'description': (None, "null"),
             'videoChannelId': (None, str(channel)),
             'thumbnailfile': (None, "null")}
    try:
        response = oauth.post(url + "/api/v1/video-playlists/",
                       files=files)
    except Exception as e:
        if hasattr(e, 'message'):
            logging.error("Error: " + str(e.message))
        else:
            logging.error("Error: " + str(e))
    if response is not None:
        if response.status_code == 200:
            jresponse = response.json()
            jresponse = jresponse['videoPlaylist']
            return jresponse['id']
        else:
            logging.error(('Peertube: Creating the playlist failed with an unexpected response: '
                           '%s') % response)
            exit(1)


def set_playlist(oauth, url, video_id, playlist_id):
    logging.info('Peertube: add video to playlist.')
    data = '{"videoId":"' + str(video_id) + '"}'

    headers = {
        'Content-Type': "application/json"
    }
    try:
        response = oauth.post(url + "/api/v1/video-playlists/"+str(playlist_id)+"/videos",
                              data=data,
                              headers=headers)
    except Exception as e:
        if hasattr(e, 'message'):
            logging.error("Error: " + str(e.message))
        else:
            logging.error("Error: " + str(e))
    if response is not None:
        if response.status_code == 200:
            logging.info('Peertube: Video is successfully added to the playlist.')
        else:
            logging.error(('Peertube: Configuring the playlist failed with an unexpected response: '
                           '%s') % response)
            exit(1)


def upload_video(oauth, secret, options):

    def get_userinfo():
        return json.loads(oauth.get(url+"/api/v1/users/me").content)

    def get_file(path):
        mimetypes.init()
        return (basename(path), open(abspath(path), 'rb'),
                mimetypes.types_map[splitext(path)[1]])

    def get_playlist(username):
        return json.loads(oauth.get(url+"/api/v1/accounts/"+username+"/video-playlists").content)

    path = options.get('--file')
    url = str(secret.get('peertube', 'peertube_url')).rstrip('/')
    user_info = get_userinfo()
    user_playlists = get_playlist(str(secret.get('peertube', 'username').lower()))

    # We need to transform fields into tuple to deal with tags as
    # MultipartEncoder does not support list refer
    # https://github.com/requests/toolbelt/issues/190 and
    # https://github.com/requests/toolbelt/issues/205
    fields = [
        ("name", options.get('--name') or splitext(basename(options.get('--file')))[0]),
        ("licence", "1"),
        ("description", options.get('--description')  or "default description"),
        ("nsfw", str(int(options.get('--nsfw')) or "0")),
        ("videofile", get_file(path))
    ]

    if options.get('--tags'):
        tags = options.get('--tags').split(',')
        for strtag in tags:
            # Empty tag crashes Peertube, so skip them
            if strtag == "":
                continue
            # Tag more than 30 chars crashes Peertube, so exit and check tags
            if len(strtag) >= 30:
                logging.warning("Peertube: Sorry, Peertube does not support tag with more than 30 characters, please reduce tag: " + strtag)
                exit(1)
            fields.append(("tags[]", strtag))

    if options.get('--category'):
        fields.append(("category", str(utils.getCategory(options.get('--category'), 'peertube'))))
    else:
        # if no category, set default to 2 (Films)
        fields.append(("category", "2"))

    if options.get('--language'):
        fields.append(("language", str(utils.getLanguage(options.get('--language'), "peertube"))))
    else:
        # if no language, set default to 1 (English)
        fields.append(("language", "en"))

    if options.get('--disable-comments'):
        fields.append(("commentsEnabled", "0"))
    else:
        fields.append(("commentsEnabled", "1"))

    privacy = None
    if options.get('--privacy'):
        privacy = options.get('--privacy').lower()

    # If peertubeAt exists, use instead of publishAt
    if options.get('--peertubeAt'):
        publishAt = options.get('--peertubeAt')
    elif options.get('--publishAt'):
        publishAt = options.get('--publishAt')

    if 'publishAt' in locals():
        publishAt = datetime.datetime.strptime(publishAt, '%Y-%m-%dT%H:%M:%S')
        tz = get_localzone()
        tz = pytz.timezone(str(tz))
        publishAt = tz.localize(publishAt).isoformat()
        fields.append(("scheduleUpdate[updateAt]", publishAt))
        fields.append(("scheduleUpdate[privacy]", str(PEERTUBE_PRIVACY["public"])))
        fields.append(("privacy", str(PEERTUBE_PRIVACY["private"])))
    else:
        fields.append(("privacy", str(PEERTUBE_PRIVACY[privacy or "private"])))

    if options.get('--thumbnail'):
        fields.append(("thumbnailfile", get_file(options.get('--thumbnail'))))
        fields.append(("previewfile", get_file(options.get('--thumbnail'))))

    if options.get('--channel'):
        channel_id = get_channel_by_name(user_info, options)
        if not channel_id and options.get('--channelCreate'):
            channel_id = create_channel(oauth, url, options)
        elif not channel_id:
            logging.warning("Channel `" + options.get('--channel') + "` is unknown, using default channel.")
            channel_id = get_default_channel(user_info)
    else:
        channel_id = get_default_channel(user_info)

    fields.append(("channelId", str(channel_id)))

    if options.get('--playlist'):
        playlist_id = get_playlist_by_name(user_playlists, options)
        if not playlist_id and options.get('--playlistCreate'):
            playlist_id = create_playlist(oauth, url, options, channel_id)
        elif not playlist_id:
            logging.warning("Playlist `" + options.get('--playlist') + "` does not exist, please set --playlistCreate"
                            " if you want to create it")
            exit(1)

    multipart_data = MultipartEncoder(fields)

    headers = {
        'Content-Type': multipart_data.content_type
    }
    response = oauth.post(url + "/api/v1/videos/upload",
                          data=multipart_data,
                          headers=headers)
    if response is not None:
        if response.status_code == 200:
            jresponse = response.json()
            jresponse = jresponse['video']
            uuid = jresponse['uuid']
            video_id = str(jresponse['id'])
            logging.info('Peertube : Video was successfully uploaded.')
            template = 'Peertube: Watch it at %s/videos/watch/%s.'
            logging.info(template % (url, uuid))
            # Upload is successful we may set playlist
            if options.get('--playlist'):
                set_playlist(oauth, url, video_id, playlist_id)
        else:
            logging.error(('Peertube: The upload failed with an unexpected response: '
                           '%s') % response)
            exit(1)


def run(options):
    secret = RawConfigParser()
    try:
        secret.read(PEERTUBE_SECRETS_FILE)
    except Exception as e:
        logging.error("Peertube: Error loading " + str(PEERTUBE_SECRETS_FILE) + ": " + str(e))
        exit(1)
    insecure_transport = secret.get('peertube', 'OAUTHLIB_INSECURE_TRANSPORT')
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = insecure_transport
    oauth = get_authenticated_service(secret)
    try:
        logging.info('Peertube: Uploading video...')
        upload_video(oauth, secret, options)
    except Exception as e:
        if hasattr(e, 'message'):
            logging.error("Peertube: Error: " + str(e.message))
        else:
            logging.error("Peertube: Error: " + str(e))
