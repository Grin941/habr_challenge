def coroutine(func):  # pragma: no cov
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return start


def cached_property(f):
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
            _ = self._property_cache[f] = f(self)
            return _
        except KeyError:
            _ = self._property_cache[f] = f(self)
            return _
    return property(get)
