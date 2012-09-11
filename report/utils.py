# encoding=utf-8
import StringIO
import calendar

import datetime
import json
import zipfile
import httplib2
import os


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


def get_data_from_url(url, username='', password=''):
    """Fetches data from the given url, if username is supplied it will apply
credentials with the given username and password.

The return value is a tuple of (response, content), the first
being and instance of the 'Response' class, the second being
a string that contains the response entity body.
    """
    http = httplib2.Http()
    if username != '':
        http.add_credentials(username, password)
    response, content = http.request(url)
    return response, content


def get_timestamp():
    """Returns unix timestamp"""
    d = datetime.datetime.now()
    return calendar.timegm(d.utctimetuple())


def download_commcare_zip_report(url, username, password):
    """Downloads commcares csv exoorts given a commcare csv export url"""
    ZIPDIR = "output"
    response, content = get_data_from_url(url, username, password)
    if response.status == 200 and\
       response['content-type'] == 'application/zip':
        zip_data = StringIO.StringIO(content)
        zf = zipfile.ZipFile(zip_data)
        path = os.path.join(ZIPDIR, '%s' % get_timestamp())
        if not os.path.exists(path):
            os.mkdir(path)
        zf.extractall(path)
        return os.path.join(path, '#.csv')
    return None
