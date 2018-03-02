#!/usr/bin/python
# coding: utf-8
# From Youtube samples : https://raw.githubusercontent.com/youtube/api-samples/master/python/upload_video.py

import argparse
import httplib
import httplib2
import os
import random
import time

import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow


# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Youtube retriables cases
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]


CLIENT_SECRETS_FILE = 'youtube_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


# Authorize the request and store authorization credentials.
def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def initialize_upload(youtube, options):
  path = options.get('--file')
  print options.get('--name')
  tags = None
  if options.get('--tags'):
    tags = options.get('--tags').split(',')

  body=dict(
    snippet=dict(
      title=options.get('--name') or os.path.splitext(os.path.basename(path))[0],
      description=options.get('--description') or "",
      tags=tags,
      categoryId=str(options.get('--category') or 1),
    ),
    status=dict(
      privacyStatus=str(options.get('--privacy') or "private"),
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=','.join(body.keys()),
    body=body,
    media_body=MediaFileUpload(path, chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print 'Uploading file...'
      status, response = request.next_chunk()
      if response is not None:
        if 'id' in response:
          print 'Video id "%s" was successfully uploaded.' % response['id']
        else:
          exit('The upload failed with an unexpected response: %s' % response)
    except HttpError, e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS, e:
      error = 'A retriable error occurred: %s' % e

    if error is not None:
      print error
      retry += 1
      if retry > MAX_RETRIES:
        exit('No longer attempting to retry.')

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print 'Sleeping %f seconds and then retrying...' % sleep_seconds
      time.sleep(sleep_seconds)


def run(options):
  youtube = get_authenticated_service()
  try:
    initialize_upload(youtube, options)
  except HttpError, e:
    print 'An HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
