# encoding=utf-8
# maintainer: katembu

import locale

from django import template
from django.template.defaultfilters import stringfilter

from report.bamboo import *
from report.models import *

locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.simple_tag
def mtitle(data):
    return data.replace("_", " ")
    
'''
@register.tag(name='dictkeys')
def dictkeys(data):
    retun data.keys()
'''

@register.simple_tag
def summary(data):
    return count_submissions(data, '')


@register.filter(name='NAdefault')
def default_na(data):
    ''' return N/A if data is None '''

    if data is None:
        return u"n/a"
    return data


@register.filter(name='numberformat')
@stringfilter
def number_format(value, precision=2, french=True):
    try:
        format = '%d'
        value = int(value)
    except:
        try:
            format = '%.' + '%df' % precision
            value = float(value)
        except:
            format = '%s'
        else:
            if value.is_integer():
                format = '%d'
                value = int(value)
    try:
        if french:
            return strnum_french(locale.format(format, value, grouping=True))
        return locale.format(format, value, grouping=True)
    except Exception:
        pass
    return value


def strnum_french(numstr):
    if locale.getdefaultlocale()[0].__str__().startswith('fr'):
        return numstr
    else:
        return numstr.replace(',', ' ').replace('.', ',')


@register.filter(name='percent')
@stringfilter
def format_percent(value, precision=2, french=True):
    if value == u'n/a':
        return value
    try:
        return number_format(float(value) * 100, precision, french) + '%'
    except:
        return value
