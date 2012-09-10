# encoding=utf-8
# This is clone of microsite bamboo utilities started by Renauld
# maintainer: katembu

import json

import requests


from report.utils import get_option, load_json, dump_json

BAMBOO_URL = 'http://bamboo.io'

class ErrorRetrievingBambooData(IOError):
    pass


class ErrorParsingBambooData(ValueError):
    pass


def get_bamboo_datasets_url(report):

    data = {'bamboo_url': get_bamboo_url()}
    return u'%(bamboo_url)s/datasets' % data


def get_bamboo_url():
    return BAMBOO_URL


def get_bamboo_ids_dataset(report):
    return get_option(report)


def get_bamboo_dataset_url(report):

    dataset = get_bamboo_ids_dataset(report)
    data = {'bamboo_url': get_bamboo_url(),
            'dataset': dataset}
    return u'%(bamboo_url)s/datasets/%(dataset)s' % data


def get_bamboo_dataset_summary_url(report):
    data = {'dataset_url': get_bamboo_dataset_url(report)}
    return u'%(dataset_url)s/summary' % data


def get_bamboo_dataset_info_url(report):
    data = {'dataset_url': get_bamboo_dataset_url(report)}
    return u'%(dataset_url)s/info' % data


def get_bamboo_dataset_calculations_url(report):
    
    dataset = get_bamboo_ids_dataset(report)
    data = {'bamboo_url': get_bamboo_url(),
            'dataset': dataset}
    return u'%(bamboo_url)s/calculations/%(dataset)s' % data


def count_submissions(report, field, method='count'):
    ''' Number of submissions for a given field.

    method is one of: '25%', '50%', '75%', 'count' (default),
                      'max', 'mean', 'min', 'std' '''

    data = {'bamboo_url': get_bamboo_url(),
            'dataset': Option.objects.get(key='bamboo_dataset',
                                          report=report).value,}

    if not all(data):
        return False

    url = get_bamboo_dataset_summary_url(report)
    
    req = requests.get(url)
    if not req.status_code in (200, 202):
        raise ErrorRetrievingBambooData

    try:
        response = json.loads(req.text)

        value = response.get(field).get('summary')
        if method in value:
            return float(value.get(method))
        else:
            return sum([int(relval) for relval in value.values()])

    except:
        raise ErrorRetrievingBambooData
    return 0


def bamboo_query(report,
                 select=None, query=None, group=None,
                 as_summary=False,
                 first=False, last=False,
                 print_url=False):

    params = {
        'select': select,
        'query': query,
        'group': group
    }

    # remove key with no value
    for key, value in params.items():
        if not value:
            params.pop(key)
        else:
            if isinstance(value, dict):
                params[key] = dump_json(value)

    if as_summary:
        url = get_bamboo_dataset_summary_url(report)
    else:
        url = get_bamboo_dataset_url(report)

    req = requests.get(url, params=params)

    # debugging
    if print_url:
        print(req.url)

    if not req.status_code in (200, 202):
        raise ErrorRetrievingBambooData(u"%d Status Code received."
                                        % req.status_code)

    try:
        response = load_json(req.text)
        if last:
            return response[-1]
        elif first:
            return response[0]
        else:
            return response 
    except Exception as e:
        print(req.text)
        raise ErrorParsingBambooData(e.message)


def bamboo_store_calculation(report, formula_name, formula):

    url = get_bamboo_dataset_calculations_url(report)

    params = {'name': formula_name,
              'formula': formula}

    req = requests.post(url, params=params)

    if not req.status_code in (200, 201, 202):
        raise ErrorRetrievingBambooData(u"%d Status Code received."
                                        % req.status_code)

    try:
        return load_json(req.text)
    except Exception as e:
        print(req.text)
        raise ErrorParsingBambooData(e.message)

