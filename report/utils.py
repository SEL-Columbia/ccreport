# encoding=utf-8

import calendar

import datetime
import json
import zipfile
import os
import requests

from requests.auth import HTTPDigestAuth
from StringIO import StringIO


class DownloadFailed(StandardError):
    pass


class ProjectUnconfigured(Exception):
    def __init__(self, project=None):
        Exception.__init__(self, u"Project “%s” is not configured." % project)
        self.project = project


def dump_json(obj, default=None):
    ''' shortcut to json dump with datetime hack '''
    def date_default(obj):
        return obj.isoformat() if isinstance(obj, datetime.datetime) else obj
    if not default:
        default = date_default
    return json.dumps(obj, default=default)


def load_json(json_str, object_hook=None):
    return json.loads(json_str, object_hook=object_hook)


def get_option(report):
    from report.models import CommcareReport
    try:
        return CommcareReport.objects.get(pk=report.pk).dataset_id
    except:
        raise ProjectUnconfigured(report)


def get_timestamp():
    """Returns unix timestamp"""
    d = datetime.datetime.now()
    return calendar.timegm(d.utctimetuple())


def download_commcare_zip_report(url, username, password):
    """Downloads commcares csv exoorts given a commcare csv export url"""
    ZIPDIR = "../output"
    curdir = os.path.dirname(os.path.realpath(__file__))
    ZIPDIR = os.path.realpath(os.path.join(curdir, ZIPDIR))
    if not os.path.exists(ZIPDIR):
        os.mkdir(ZIPDIR)
    response = requests.get(url, auth=HTTPDigestAuth(username, password))
    if response.status_code == 200 and\
       response.headers.get('content-type', '') == 'application/zip':
        zip_data = StringIO(response.content)
        zf = zipfile.ZipFile(zip_data)
        path = os.path.join(ZIPDIR, '%s' % get_timestamp())
        if not os.path.exists(path):
            os.mkdir(path)
        zf.extractall(path)
        return os.path.join(path, '#.csv')
    return None
