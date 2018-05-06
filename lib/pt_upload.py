#!/usr/bin/python
# coding: utf-8

import os
import mimetypes
import json
import logging
from os.path import splitext, basename, abspath

from ConfigParser import RawConfigParser
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient
from requests_toolbelt.multipart.encoder import MultipartEncoder

import utils

PEERTUBE_SECRETS_FILE = 'peertube_secret'
PEERTUBE_PRIVACY = {
    "public": 1,
    "unlisted": 2,
    "private": 3
}


def get_authenticated_service(secret):
    peertube_url = str(secret.get('peertube', 'peertube_url'))

    oauth_client = LegacyApplicationClient(
        client_id=str(secret.get('peertube', 'client_id'))
    )
    oauth = OAuth2Session(client=oauth_client)
    oauth.fetch_token(
        token_url=peertube_url + '/api/v1/users/token',
        # lower as peertube does not store uppecase for pseudo
        username=str(secret.get('peertube', 'username').lower()),
        password=str(secret.get('peertube', 'password')),
        client_id=str(secret.get('peertube', 'client_id')),
        client_secret=str(secret.get('peertube', 'client_secret'))
    )

    return oauth


def upload_video(oauth, secret, options):

    def get_userinfo():
        user_info = json.loads(oauth.get(url + "/api/v1/users/me").content)
        return str(user_info["id"])

    def get_videofile(path):
        mimetypes.init()
        return (basename(path), open(abspath(path), 'rb'),
                mimetypes.types_map[splitext(path)[1]])

    path = options.get('--file')
    url = secret.get('peertube', 'peertube_url')

    # We need to transform fields into tuple to deal with tags as
    # MultipartEncoder does not support list refer
    # https://github.com/requests/toolbelt/issues/190 and
    # https://github.com/requests/toolbelt/issues/205
    fields = [
        ("name", options.get('--name') or splitext(basename(path))[0]),
        ("licence", "1"),
        ("description", options.get('--description')  or "default description"),
        ("nsfw", str(int(options.get('--nsfw')) or "0")),
        ("channelId", get_userinfo()),
        ("videofile", get_videofile(path))
    ]

    if options.get('--tags'):
        tags = options.get('--tags').split(',')
        for strtag in tags:
            # Empty tag crashes Peertube, so skip them
            if strtag == "":
                continue
            # Tag more than 30 chars crashes Peertube, so exit and check tags
            if len(strtag) >= 30:
                logging.warning("Sorry, Peertube does not support tag with more than 30 characters, please reduce your tag size")
                exit(1)
            # If Mastodon compatibility is enabled, clean tags from special characters
            if options.get('--mt'):
                strtag = utils.mastodonTag(strtag)
            fields.append(("tags", strtag))

    if options.get('--category'):
        fields.append(("category", str(utils.getCategory(options.get('--category'), 'peertube'))))
    else:
        # if no category, set default to 2 (Films)
        fields.append(("category", "2"))

    if options.get('--language'):
        fields.append(("language", str(utils.getLanguage(options.get('--language'), "peertube"))))
    else:
        # if no language, set default to 1 (English)
        fields.append(("language", "1"))

    if options.get('--privacy'):
        fields.append(("privacy", str(PEERTUBE_PRIVACY[options.get('--privacy').lower()])))
    else:
        fields.append(("privacy", "3"))

    if options.get('--disable-comments'):
        fields.append(("commentsEnabled", "0"))
    else:
        fields.append(("commentsEnabled", "1"))

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
            idvideo = str(jresponse['id'])
            template = ('Peertube : Video was successfully uploaded.\n'
                        'Watch it at %s/videos/watch/%s.')
            logging.info(template % (url, uuid))
        else:
            logging.error(('Peertube : The upload failed with an unexpected response: '
                           '%s') % response)
            exit(1)

    if options.get('--publishAt'):
        utils.publishAt(str(options.get('--publishAt')), oauth, url, idvideo)


def run(options):
    secret = RawConfigParser()
    try:
        secret.read(PEERTUBE_SECRETS_FILE)
    except Exception as e:
        logging.error("Error loading " + str(PEERTUBE_SECRETS_FILE) + ": " + str(e))
        exit(1)
    insecure_transport = secret.get('peertube', 'OAUTHLIB_INSECURE_TRANSPORT')
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = insecure_transport
    oauth = get_authenticated_service(secret)
    try:
        logging.info('Peertube : Uploading file...')
        upload_video(oauth, secret, options)
    except Exception as e:
        if hasattr(e, 'message'):
            logging.error("Error: " + str(e.message))
        else:
            logging.error("Error: " + str(e))
