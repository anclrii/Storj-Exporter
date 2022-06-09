from collections import Counter

def _sum_list_of_dicts(list, path, default={}):
    _counter = Counter()
    try:
        for i in list:
            _counter.update(i[path])
        return dict(_counter)
    except Exception:
        return default

def _safe_list_get(list, idx, default={}):
    try:
        return list[idx]
    except Exception:
        return default