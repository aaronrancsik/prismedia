#!/usr/bin/python
# coding: utf-8

import os
import mimetypes
import json
from os.path import splitext, basename, abspath

from ConfigParser import RawConfigParser
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient
from requests_toolbelt.multipart.encoder import MultipartEncoder

import utils

PEERTUBE_SECRETS_FILE = 'peertube_secret'


def get_authenticated_service(config):
    peertube_url = str(config.get('peertube', 'peertube_url'))

    oauth_client = LegacyApplicationClient(
        client_id=str(config.get('peertube', 'client_id'))
    )
    oauth = OAuth2Session(client=oauth_client)
    oauth.fetch_token(
        token_url=peertube_url + '/api/v1/users/token',
        # lower as peertube does not store uppecase for pseudo
        username=str(config.get('peertube', 'username').lower()),
        password=str(config.get('peertube', 'password')),
        client_id=str(config.get('peertube', 'client_id')),
        client_secret=str(config.get('peertube', 'client_secret'))
    )
    return oauth


def upload_video(oauth, config, options):

    def get_userinfo():
        user_info = json.loads(oauth.get(url + "/api/v1/users/me").content)
        return str(user_info["id"])

    def get_videofile(path):
        mimetypes.init()
        return (basename(path), open(abspath(path), 'rb'),
                mimetypes.types_map[splitext(path)[1]])

    path = options.get('--file')
    url = config.get('peertube', 'peertube_url')
    tags = None

    # We need to transform fields into tuple to deal with tags as
    # MultipartEncoder does not support list refer
    # https://github.com/requests/toolbelt/issues/190 and
    # https://github.com/requests/toolbelt/issues/205
    fields = [
        ("name", options.get('--name') or splitext(basename(path))[0]),
        # look at the list numbers at /videos/licences
        ("licence", str(options.get('--licence') or 1)),
        ("description", options.get('--description') or "default description"),
        # look at the list numbers at /videos/privacies
        ("privacy", str(options.get('--privacy') or 3)),
        ("nsfw", str(options.get('--nsfw') or 0)),
        ("commentsEnabled", "1"),
        ("channelId", get_userinfo()),
        ("videofile", get_videofile(path))
    ]

    if options.get('--tags'):
        tags = options.get('--tags').split(',')
        for strtags in tags:
            fields.append(("tags", strtags))

    if options.get('--category'):
        fields.append(("category", str(utils.getCategory(options.get('--category'), 'peertube'))))
    else:
        #if no category, set default to 2 (Films)
        fields.append(("category", "2"))

    multipart_data = MultipartEncoder(fields)

    headers = {
        'Content-Type': multipart_data.content_type
    }

    response = oauth.post(url + "/api/v1/videos/upload",
                          data=multipart_data,
                          headers=headers)
    if response is not None:
        if response.status_code == 200:
            print('Peertube : Video was successfully uploaded.')
        else:
            exit(('Peertube : The upload failed with an unexpected response: '
                  '%s') % response)


def run(options):
    config = RawConfigParser()
    config.read(PEERTUBE_SECRETS_FILE)
    insecure_transport = config.get('peertube', 'OAUTHLIB_INSECURE_TRANSPORT')
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = insecure_transport
    oauth = get_authenticated_service(config)
    try:
        print('Peertube : Uploading file...')
        upload_video(oauth, config, options)
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)
