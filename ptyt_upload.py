#!/usr/bin/python
# coding: utf-8

"""
ptyt_upload - tool to upload videos to Peertube and Youtube

Usage: 
  ptyt_upload.py --file=<FILE> [options]
  ptyt_upload.py -h | --help
  ptyt_upload.py --version

Options:
  --name=NAME  Name of the video to upload. default to video file name
  -d, --description=STRING  Description of the video.
  -t, --tags=STRING  Tags for the video. comma separated
  -h --help  Show this help.
  --version  Show version.
  


"""
import argparse
from docopt import docopt
try:
    from schema import Schema, And, Or, Use, Optional, SchemaError
except ImportError:
    exit('This program requires that the `schema` data-validation library'
         ' is installed: \n'
         'see https://github.com/halst/schema\n')
try:
    import magic
except ImportError:
    exit('This program requires that the `magic` library'
         ' is installed, NOT the Python bindings to libmagic API \n'
         'see https://github.com/ahupp/python-magic\n')

VERSION="ptyt 0.1-alpha"
VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')

def validateVideo(path):
    supported_types = ['video/mp4']
    if magic.from_file(path, mime=True) in supported_types:
        return path
    else:
        return False

if __name__ == '__main__':

    #Allows you to a relative import from the parent folder
    import os.path, sys
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))+"/lib") 

    import yt_upload
    import pt_upload

    options = docopt(__doc__, version=VERSION)

    schema = Schema({
        '--file': And(str, lambda s: validateVideo(s), error='file is not supported, please use mp4'),
        Optional('--name'): Or(None, And(str, lambda x: not x.isdigit(), error="The video name should be a string")),
        Optional('--description'): Or(None, And(str, lambda x: not x.isdigit(), error="The video name should be a string")),
        Optional('--tags'): Or(None, And(str, lambda x: not x.isdigit(), error="Tags should be a string")),
        '--help': bool,
        '--version': bool
    })

    try:
        options = schema.validate(options)
    except SchemaError as e:
        exit(e)
    
    yt_upload.run(options)
    pt_upload.run(options)