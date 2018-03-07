#!/usr/bin/python
# coding: utf-8

import os
import mimetypes
import httplib
import httplib2
import json

from ConfigParser import RawConfigParser
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient
from requests_toolbelt.multipart.encoder import MultipartEncoder

PEERTUBE_SECRETS_FILE = 'peertube_secret'

def get_authenticated_service(config):
    oauth = OAuth2Session(client=LegacyApplicationClient(client_id=str(config.get('peertube', 'client_id'))))
    oauth.fetch_token(token_url=str(config.get('peertube', 'peertube_url')) + '/api/v1/users/token',
                      username=str(config.get('peertube', 'username').lower()), #lower as peertube does not store uppecase for pseudo
                      password=str(config.get('peertube', 'password')),
                      client_id=str(config.get('peertube', 'client_id')),
                      client_secret=str(config.get('peertube', 'client_secret'))
                      )
    return oauth

def upload_video(oauth, config, options):

    def get_userinfo():
        user_info = json.loads(oauth.get(url+"/api/v1/users/me").content)
        return str(user_info["id"])

    def get_videofile(path):
        mimetypes.init()
        return (os.path.basename(path), open(os.path.abspath(path), 'rb'),
                mimetypes.types_map[os.path.splitext(path)[1]])

    path = options.get('--file')
    url = config.get('peertube', 'peertube_url')
    fields = {
        "name": options.get('--name') or os.path.splitext(os.path.basename(path))[0],
        "category": str(options.get('--category') or 1),  # look at the list numbers at /videos/categories
        "licence": str(options.get('--licence') or 1),  # look at the list numbers at /videos/licences
        "description": options.get('--description') or "",
        "privacy": str(options.get('--privacy') or 3),  # look at the list numbers at /videos/privacies
        "nsfw": str(options.get('--nsfw') or 0),
        "commentsEnabled": "1",
        "channelId": get_userinfo(),
        "videofile": get_videofile(path)  # beware, see validateVideo for supported types
    }

    multipart_data = MultipartEncoder(fields=fields)
    headers = {
        'Content-Type': multipart_data.content_type
    }

    response = oauth.post(config.get('peertube', 'peertube_url')+"/api/v1/videos/upload", data=multipart_data, headers=headers)
    if response is not None:
        if response.status_code == 200:
          print 'Peertube : Video was successfully uploaded.'
        else:
          exit('Peertube : The upload failed with an unexpected response: %s' % response)


def run(options):
    config = RawConfigParser()
    config.read(PEERTUBE_SECRETS_FILE)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = config.get('peertube', 'OAUTHLIB_INSECURE_TRANSPORT')
    oauth = get_authenticated_service(config)
    try:
        print 'Peertube : Uploading file...'
        upload_video(oauth, config, options)
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)