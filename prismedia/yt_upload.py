#!/usr/bin/env python
# coding: utf-8
# From Youtube samples : https://raw.githubusercontent.com/youtube/api-samples/master/python/upload_video.py  # noqa

import http.client
import httplib2
import random
import time
import copy
import json
from os.path import splitext, basename, exists
import os
import google.oauth2.credentials
import datetime
import pytz
import logging
from tzlocal import get_localzone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow


from . import utils
logger = logging.getLogger('Prismedia')

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Youtube retriables cases
RETRIABLE_EXCEPTIONS = (
    IOError,
    httplib2.HttpLib2Error,
    http.client.NotConnected,
    http.client.IncompleteRead,
    http.client.ImproperConnectionState,
    http.client.CannotSendRequest,
    http.client.CannotSendHeader,
    http.client.ResponseNotReady,
    http.client.BadStatusLine,
)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


CLIENT_SECRETS_FILE = 'youtube_secret.json'
CREDENTIALS_PATH = ".youtube_credentials.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.upload', 'https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


# Authorize the request and store authorization credentials.
def get_authenticated_service():
    check_authenticated_scopes()
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    if exists(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, 'r') as f:
            credential_params = json.load(f)
            credentials = google.oauth2.credentials.Credentials(
                credential_params["token"],
                refresh_token=credential_params["_refresh_token"],
                token_uri=credential_params["_token_uri"],
                client_id=credential_params["_client_id"],
                client_secret=credential_params["_client_secret"]
            )
    else:
        credentials = flow.run_console()
        with open(CREDENTIALS_PATH, 'w') as f:
            p = copy.deepcopy(vars(credentials))
            del p["expiry"]
            json.dump(p, f)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials,  cache_discovery=False)


def check_authenticated_scopes():
    if exists(CREDENTIALS_PATH):
        with open(CREDENTIALS_PATH, 'r') as f:
            credential_params = json.load(f)
            # Check if all scopes are present
            if credential_params["_scopes"] != SCOPES:
                logger.warning("Youtube: Credentials are obsolete, need to re-authenticate.")
                os.remove(CREDENTIALS_PATH)


def initialize_upload(youtube, options):
    path = options.get('--file')
    tags = None
    if options.get('--tags'):
        tags = options.get('--tags').split(',')

    category = None
    if options.get('--category'):
        category = utils.getCategory(options.get('--category'), 'youtube')

    language = None
    if options.get('--language'):
        language = utils.getLanguage(options.get('--language'), "youtube")

    license = None
    if options.get('--cca'):
        license = "creativeCommon"

    body = {
        "snippet": {
            "title": options.get('--name') or splitext(basename(path))[0],
            "description": options.get('--description') or "default description",
            "tags": tags,
            # if no category, set default to 1 (Films)
            "categoryId": str(category or 1),
            "defaultAudioLanguage": str(language or 'en')
        },
        "status": {
            "privacyStatus": str(options.get('--privacy') or "private"),
            "license": str(license or "youtube"),
        }
    }

    # If peertubeAt exists, use instead of publishAt
    if options.get('--youtubeAt'):
        publishAt = options.get('--youtubeAt')
    elif options.get('--publishAt'):
        publishAt = options.get('--publishAt')

    if 'publishAt' in locals():
        # Youtube needs microsecond and the local timezone from ISO 8601
        publishAt = publishAt + ".000001"
        publishAt = datetime.datetime.strptime(publishAt, '%Y-%m-%dT%H:%M:%S.%f')
        tz = get_localzone()
        tz = pytz.timezone(str(tz))
        publishAt = tz.localize(publishAt).isoformat()
        body['status']['publishAt'] = str(publishAt)

    if options.get('--playlist'):
        playlist_id = get_playlist_by_name(youtube, options.get('--playlist'))
        if not playlist_id and options.get('--playlistCreate'):
            playlist_id = create_playlist(youtube, options.get('--playlist'))
        elif not playlist_id:
            logger.warning("Youtube: Playlist `" + options.get('--playlist') + "` is unknown.")
            logger.warning("Youtube: If you want to create it, set the --playlistCreate option.")
            playlist_id = ""
    else:
        playlist_id = ""

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
        part=','.join(list(body.keys())),
        body=body,
        media_body=MediaFileUpload(path, chunksize=-1, resumable=True)
    )
    video_id = resumable_upload(insert_request, 'video', 'insert', options)

    # If we get a video_id, upload is successful and we are able to set thumbnail
    if video_id and options.get('--thumbnail'):
        set_thumbnail(options, youtube, options.get('--thumbnail'), videoId=video_id)

    # If we get a video_id and a playlist_id, upload is successful and we are able to set playlist
    if video_id and playlist_id != "":
        set_playlist(youtube, playlist_id, video_id)


def get_playlist_by_name(youtube, playlist_name):
    response = youtube.playlists().list(
        part='snippet,id',
        mine=True,
        maxResults=50
    ).execute()
    for playlist in response["items"]:
        if playlist["snippet"]['title'] == playlist_name:
            return playlist['id']


def create_playlist(youtube, playlist_name):
    template = 'Youtube: Playlist %s does not exist, creating it.'
    logger.info(template % (str(playlist_name)))
    resources = build_resource({'snippet.title': playlist_name,
                                'snippet.description': '',
                                'status.privacyStatus': 'public'})
    response = youtube.playlists().insert(
        body=resources,
        part='status,snippet,id'
    ).execute()
    return response["id"]


def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into "snippet" and "title", where
        # "snippet" will be an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]

            # For properties that have array values, convert a name like
            # "snippet.tags[]" to snippet.tags, and set a flag to handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key)-2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                # Leave properties without values out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title", but the resource does
                # not yet have a "snippet" object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the next time through the
                # "for pa in range ..." loop, we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description", and the resource
                # already has a "snippet" object.
                ref = ref[key]
    return resource


def set_thumbnail(options, youtube, media_file, **kwargs):
    kwargs = utils.remove_empty_kwargs(**kwargs)
    request = youtube.thumbnails().set(
        media_body=MediaFileUpload(media_file, chunksize=-1,
                                   resumable=True),
        **kwargs
    )

    return resumable_upload(request, 'thumbnail', 'set', options)


def set_playlist(youtube, playlist_id, video_id):
    logger.info('Youtube: Configuring playlist...')
    resource = build_resource({'snippet.playlistId': playlist_id,
                               'snippet.resourceId.kind': 'youtube#video',
                               'snippet.resourceId.videoId': video_id,
                               'snippet.position': ''}
                              )
    try:
        youtube.playlistItems().insert(
            body=resource,
            part='snippet'
        ).execute()
    except Exception as e:
        # Workaround while youtube API is broken, see issue #47 for details
        if e.resp.status != 404 and "Video not found" not in str(e):
            if hasattr(e, 'message'):
                logger.critical("Youtube: " + str(e.message))
                exit(1)
            else:
                logger.critical("Youtube: " + str(e))
                exit(1)
    logger.info('Youtube: Video is correctly added to the playlist.')


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(request, resource, method, options):
    response = None
    error = None
    retry = 0
    logger_stdout = None
    if options.get('--url-only') or options.get('--batch'):
        logger_stdout = logging.getLogger('stdoutlogs')
    while response is None:
        try:
            template = 'Youtube: Uploading %s...'
            logger.info(template % resource)
            status, response = request.next_chunk()
            if response is not None:
                if method == 'insert' and 'id' in response:
                    logger.info('Youtube : Video was successfully uploaded.')
                    template = 'Youtube: Watch it at https://youtu.be/%s (post-encoding could take some time)'
                    logger.info(template % response['id'])
                    template_stdout = 'https://youtu.be/%s'
                    if options.get('--url-only'):
                        logger_stdout.info(template_stdout % response['id'])
                    elif options.get('--batch'):
                        logger_stdout.info("Youtube: " + template_stdout % response['id'])
                    return response['id']
                elif method != 'insert' or "id" not in response:
                    logger.info('Youtube: Thumbnail was successfully set.')
                else:
                    template = ('Youtube : The upload failed with an '
                                'unexpected response: %s')
                    logger.critical(template % response)
                    exit(1)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                template = 'Youtube : A retriable HTTP error %d occurred:\n%s'
                error = template % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'Youtube : A retriable error occurred: %s' % e

    if error is not None:
        logger.warning(error)
        retry += 1
        if retry > MAX_RETRIES:
            logger.error('Youtube : No longer attempting to retry.')

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        logger.warning('Youtube : Sleeping %f seconds and then retrying...'
              % sleep_seconds)
        time.sleep(sleep_seconds)


def run(options):
    youtube = get_authenticated_service()
    try:
        initialize_upload(youtube, options)
    except HttpError as e:
        logger.error('Youtube : An HTTP error %d occurred:\n%s' % (e.resp.status,
                                                            e.content))
