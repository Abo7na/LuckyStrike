import time

_RATE_LIMITS = {}


def allow(rate_key, limit_seconds=3, max_calls=1):
    now = time.time()
    bucket = _RATE_LIMITS.setdefault(rate_key, [])
    bucket[:] = [ts for ts in bucket if ts > now - limit_seconds]
    if len(bucket) >= max_calls:
        return False
    bucket.append(now)
    return True
