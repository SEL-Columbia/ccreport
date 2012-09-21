import inspect
import sys
from report.indicators.MalariaIndicator import MalariaIndicator


def get_indicator_list():
    """return a list of dict with Indicator info"""
    _ind_list = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            for n, o in inspect.getmembers(obj):
                if inspect.ismethod(o) and n.endswith('_indicator'):
                    doc = o.__doc__
                    _ind = {
                        'class': obj, 'func': o, 'description': doc,
                        'name': obj.__name__ + '.' + o.__name__, 'data': ''
                    }
                    _ind_list.append(_ind)
    return _ind_list

def generate_indicators(indicator_list, report):
    """returns a list of indicators populated with calculations"""
    if not indicator_list:
        return []
    assert type(indicator_list) == list
    assert 'func' in indicator_list[0]
    data_list = []
    for indicator in indicator_list:
        indicator.update({'data': indicator['func'](report)})
        data_list.append(indicator)
    return data_list