from collections import Counter
import json


def jsonFileLoader(filename):
    def loader(req, context):
        with open(filename, 'r') as f:
            return json.loads(f.read())
    return loader

def sum_list_of_dicts(list, path, default={}):
    _counter = Counter()
    try:
        for i in list:
            _counter.update(i[path])
        return dict(_counter)
    except Exception:
        return default

def safe_list_get(list, idx, default={}):
    try:
        return list[idx]
    except Exception:
        return default

def to_float(value):
    try:
        value = float(value)
    except Exception:
        value = None
    return value

def nested_get(input_dict, nested_path):
    internal_dict_value = input_dict
    for k in nested_path:
        internal_dict_value = internal_dict_value.get(k, None)
        if internal_dict_value is None:
            return None
    return internal_dict_value
