# encoding=utf-8

import datetime
import json


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
    from report.models import CommcareReportURL
    
    try:
        return CommcareReportURL.objects.get(pk=report.pk).dataset_id
    except:
        raise ProjectUnconfigured(project)
