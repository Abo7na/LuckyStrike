import threading

_locks = {}


def get_lock(key):
    if key not in _locks:
        _locks[key] = threading.RLock()
    return _locks[key]
