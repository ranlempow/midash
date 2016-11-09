from midash import _
from collections import namedtuple as _namedtuple

_CacheInfo = _namedtuple("CacheInfo", ["hits", "misses", "currsize"])

class _HashedSeq(list):
    """ This class guarantees that hash() will be called no more than once
        per element.  This is important because the lru_cache() will hash
        the key multiple times on a cache miss.
    """
    __slots__ = 'hashvalue'
    def __init__(self, tup, hash=hash):
        self[:] = tup
        self.hashvalue = hash(tup)
    
    def __hash__(self):
        return self.hashvalue
        
def memoize(user_function, _CacheInfo=_CacheInfo):
    cache = {}
    hits = misses = 0
    cache_get = cache.get    # bound method to lookup a key or return None

    def wrapper(*args):
        # Simple caching without ordering or size limit
        nonlocal hits, misses
        key = _HashedSeq(args)
        result = cache_get(key, _.none)
        if result is not _.none:
            hits += 1
            return result
        result = user_function(*args)
        cache[key] = result
        misses += 1
        return result
    
    def cache_info():
        """Report cache statistics"""
        return _CacheInfo(hits, misses, len(cache))

    def cache_clear():
        """Clear the cache and cache statistics"""
        nonlocal hits, misses
        cache.clear()
        hits = misses = 0
            
    wrapper.cache_info = cache_info
    wrapper.cache_clear = cache_clear
    return wrapper
    
    