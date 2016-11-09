from midash import _
_.require('lang')
none = _.none

import operator
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
        result = cache_get(key, none)
        if result is not none:
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
    
    
class _CloseVariable:
    def __init__(self, pos, func_t=None):
        self.func_t = func_t or (lambda x: x)
        self.pos = pos
        
    def __call__(self, t=None):
        return _CloseVariable(self.pos, t)
        
    def transform(self, args):
        return self.func_t( *(args[i] for i in self.pos) )
        
        
ARG1 = _CloseVariable([0])
ARG2 = _CloseVariable([1])
ARG3 = _CloseVariable([2])
ARG12 = _CloseVariable([0,1])
ARG13 = _CloseVariable([0,2])
ARG23 = _CloseVariable([1,2])


class _ComposerWrapperFunc:
    def __init__(self, composer, func):
        self.composer = composer
        self.func = func
        self.args = ()
        self.isNeedTransfrom = False
        
    def __call__(self, *args):
        self.args = args
        # TODO: !!!
        self.isNeedTransfrom = any( isinstance(v, _CloseVariable) for v in args )
        return self.composer
        
class _Composer:
    def __init__(self, module):
        self.chain = []
        self.module = module
        
    def __getattr__(self, name):
        func = self.module.__dict__.get(name) #('{}_'.format(name))
        assert( func is not None )
        assert( callable(func) )
        newc = _Composer(self.module)
        newc.chain = self.chain[:]
        wrapper = _ComposerWrapperFunc(newc, func)
        newc.chain.append(wrapper)
        return wrapper

    def __call__(self):
        import functools
        # TODO: 預先執行參數變換
        def chained(func, wrapper):
            if   func is None and not wrapper.isNeedTransfrom:
                f = wrapper.func
            elif func is None and     wrapper.isNeedTransfrom:
                def f(obj, *args):
                    return wrapper.func(obj, *map(lambda a: a.transform(args) if isinstance(a, _CloseVariable) else a, w_args))
            elif                  not wrapper.isNeedTransfrom:
                def f(obj, *args):
                    return wrapper.func(func(obj, *args))
            else:
                def f(obj, *args):
                    return wrapper.func(func(obj, *args), *map(lambda a: a.transform(args) if isinstance(a, _CloseVariable) else a, w_args))
            return f
        return functools.reduce(chained, self.chain, None)

def composeWith(module):
    return _Composer(module)
    
    
    
    
    
    
    
    
    
    

@memoize
def _getFunctionArgsLength(func):
    import inspect
    sig = inspect.signature(func)
    i = 0
    for param in sig.parameters.values():
        if param.kind == param.POSITIONAL_OR_KEYWORD:
            i += 1
    return i
    
    

def spread(func, n):
    """
    Creates a function that invokes func with the this binding of the create function and an array of arguments much like Function#apply.
    """
    if n == 0: return lambda it: func(*it)
    if n == 1: return lambda v1, it: func(v1, *it)
    if n == 2: return lambda v1, v2, it: func(v1, v2, *it)
    if n == 3: return lambda v1, v2, v3, it: func(v1, v2, v3, *it)
    
def rest(func, n=None):
    """
    Creates a function that invokes func with the this binding of the created function and arguments from start and beyond provided as an array.
    """
    n = n if n is not None else _getFunctionArgsLength(func) - 1
    if n == 0: return lambda *it: func(iter(it))
    if n == 1: return lambda v1, *it: func(v1, iter(it))
    if n == 2: return lambda v1, v2, *it: func(v1, v2, iter(it))
    if n == 3: return lambda v1, v2, v3, *it: func(v1, v2, v3, iter(it))
    
def overArgs(func, transforms, n=0):
    """
    Creates a function that invokes func with its arguments transformed.
    only after nth args will be transformed. 
    """
    if n == 0: return lambda *it: func(*transforms(iter(it)))
    if n == 1: return lambda v1, *it: func(v1, *transforms(iter(it)))
    if n == 2: return lambda v1, v2, *it: func(v1, v2, *transforms(iter(it)))
    if n == 3: return lambda v1, v2, v3, *it: func(v1, v2, v3, *transforms(iter(it)))

def countArgs(func):
    return _getFunctionArgsLength(func)
    
    
def _identity(*v):
    if len(v) == 1:
        return v[0]
    return v


class _PlaceHolder():
    def __init__(self, i, transformer=None):
        self.i = i
        self.transformer = transformer or _identity
        
    def __call__(self, transformer=None):
        return _PlaceHolder(self.i, transformer)
        
    def transform(self, argsList):
        return self.transformer( *(argsList[i] for i in self.i) )
        
    def __repr__(self):
        return 'p' + str(self.i)
        
    def __hash__(self):
        return self.i
        
class _BindArgument():
    def __init__(self, i):
        self.i = i
        
    def __repr__(self):
        return 'a' + str(self.i)
        
    def __hash__(self):
        return self.i
    
_1 = _PlaceHolder(1)
_2 = _PlaceHolder(2)
_3 = _PlaceHolder(3)
_4 = _PlaceHolder(4)
_5 = _PlaceHolder(5)
_6 = _PlaceHolder(6)

_needcurry = object()

@memoize
def _partialFunctionCreator(shape, curried=False):
    # TODO??: r=None -> r=_optional
    
    purePlaceholders = tuple(filter(lambda v: isinstance(v, _PlaceHolder), shape))
    numberOfPlaceholder = len(purePlaceholders)
    #purePlaceholders = (_1, _2, _3, _4, _5, _6)[:numberOfPlaceholder]
    purePlaceholders = sorted(purePlaceholders, key=lambda v: v.i)
    
    def createParticalString(head='', tail=','):
        argstrs = list(filter(lambda v: isinstance(v, _BindArgument), shape))
        return head + ', '.join( map(str, argstrs) ) + tail if argstrs else ''
        
    def createArgString(start=0, curried=curried, head='', tail=','):
        argstrs = list( map(('{0}=_needcurry' if curried else '{0}').format, purePlaceholders[start:]) )
        return head + ', '.join( argstrs ) + tail if argstrs else ''
        
    def createParamString(head='', tail=','):
        return head + ', '.join( map(str, shape) ) + tail if shape else ''
        
    def createBodyString():
        """def wrapper(f, a): 
            def wrap({0}, *args):
                return f({1}, *args)
            return wrap"""
        return "        return f({0} *args)".format(createParamString())
        
    def createCurryBodyString():
        """
        def wrapper(f, a1, a2):
            def wrap(p1=_needcurry, p2=_needcurry, *args):
                if p2 is not _needcurry:
                    return f(a1, p1, a2, p2, *args)
                if p1 is not _needcurry:
                    return lambda p2=_needcurry, *args: wrap(p1, p2, *args)
                return wrap
            return wrap
        """
        currybody = ""
        # finish return
        if len(purePlaceholders) > 0:
            currybody = "        if {0} is not _needcurry: return f({1} *args)\n".format(purePlaceholders[-1], createParamString())
        
        
        # curring return
        if len(purePlaceholders) > 1:
            for i in range(len(purePlaceholders)-2, -1, -1):
                currybody += "        elif {0} is not _needcurry: return lambda {1} *args: wrap({2} *args)\n".format(
                        purePlaceholders[i],
                        createArgString(i+1, curried=True),
                        createArgString(0, curried=False))
        # origin return
        currybody += "        return wrap"
        
        return currybody
        
    body = """def wrapper(f {0}): 
    def wrap({1} *args):\n{2}
    return wrap""".format(
            createParticalString(head=',', tail=''),
            createArgString(), 
            (createCurryBodyString if curried else createBodyString)())
    
    # print(body)
    g = {'_needcurry': _needcurry}
    exec(body, globals(), g)
    return g['wrapper']
    
    
    
def _reshape(shape, nargs, rearg, reverse):
    shape = list(shape)
    _number_of_placeholder = len(list(filter(lambda v: isinstance(v, _PlaceHolder), shape)))
    
    # initial reorder list
    rearg =  tuple(range(1, len(shape) + 1)) if rearg is None else tuple(rearg)
    assert( 0 not in rearg )
    
    # patch shortage Placeholder
    if nargs is None:
        nargs = max(rearg)
    # print(nargs)
    if nargs >= _number_of_placeholder:
        shape.extend((_1, _2, _3, _4, _5, _6)[_number_of_placeholder : nargs - 1])
    else:
        shape = list(filter(lambda v: isinstance(v, _BindArgument) or v.i <= nargs, shape))
    
    # reordering
    reordered = []
    for src in rearg:
        assert( src - 1 < len(shape) )
        reordered.append( shape[src - 1] )
            
    shape = reordered
    if reverse:
        shape = reversed(shape)
    shape = tuple(shape)
    return shape
    
def _createWrapper(func, partials, shape, curried):
        
    # pick binded argument from argList
    args = []
    for v in shape:
        if isinstance(v, _BindArgument):
            args.append(partials[v.i - 1])
            
            
    wrapper = _partialFunctionCreator(shape, curried)(func, *args)
    wrapper._wrapped = (func, partials, shape, curried)
    return wrapper
    
def _secendPartial(_func, partials, nargs, rearg, reverse, curried):
    func, perv_partials, prev_shape, prev_curried = _func._wrapped
    perv_partials = list(perv_partials)
    prev_shape = list(prev_shape)
    
    view = []
    for i, v in enumerate(prev_shape):
        if isinstance(v, _PlaceHolder):
            view.append((i, v))
            
    for i, p in enumerate(partials):
        # TODO: !!!!!!
        prev_i, v = view[i]
        if isinstance(p, _PlaceHolder):
            prev_shape[prev_i] = v
        else:
            perv_partials.append(p)
            prev_shape[prev_i] = _BindArgument(len(perv_partials))
            
    
    partials = tuple(perv_partials)
    shape = _reshape(prev_shape, nargs, rearg, reverse)
    print(partials, shape, prev_shape, _func._wrapped[2])
    curried = prev_curried if curried is None else curried
    
    return _createWrapper(func, partials, shape, curried)
    
    
def _partial(func, *partials, nargs=None, rearg=None, reverse=False, curried=None):
    if hasattr(func, '_wrapped'):
        return _secendPartial(func, partials, nargs, rearg, reverse, curried)
    shape = []
    
    # transform to BindArgument
    for i, v in enumerate(partials):
        if isinstance(v, _PlaceHolder):
            shape.append(v)
        else:
            shape.append(_BindArgument(i+1))
            
    shape = _reshape(shape, nargs, rearg, reverse)
    curried = bool(curried)
    return _createWrapper(func, partials, shape, curried)
    
    

def partial(func, *partials):       return _partial(func, *partials)
def partialRight(func, *partials):  return _partial(func, *partials, reverse=True)
def flip(func):                     return _partial(func, reverse=True)
def uncurry(func):                  return _partial(func, curried=False)
def curry(func, *partials):         return _partial(func, *partials, curried=True)
def curryRight(func, *partials):    return _partial(func, *partials, reverse=True, curried=True)
def ary(func, n, *partials):        return _partial(func, *partials, nargs=n)
def unary(func):                    return _partial(func, nargs=1)
def rearg(func, indexes):           return _partial(func, rearg=indexes)
def negate(func):                   return lambda v: not func(v)



def test_partial():
    """
    >>> makeList = lambda *args: list(args)
    
    # >>> p = _partial(makeList, 100, 200, nargs=2)
    # >>> p(0, 300)
    # [100, 200, 0, 300]
    
    # >>> p = _partial(makeList, 100, _1, 200, _2)
    # >>> p(0, 300)
    # [100, 0, 200, 300]
    
    >>> p = _partial(makeList, 100, _1, 200, _2, rearg=[5,4,2,1], curried=True)
    
    # >>> p2 = _partial(p, curried=False)
    # >>> tuple(p()(0)(300)(400)) == tuple(p2(0, 300, 400))
    # True
    
    # >>> p2(0, 300, 400)
    # [400, 300, 0, 100]
    
    >>> p = _partial(p, 500, curried=False)
    >>> p(1, 2)
    [2, 1, 500, 100]
    
    
    >>> p = _partial(makeList, 100, _1, 200, _2, curried=True)
    >>> p = _partial(p, 500, curried=False)
    >>> p(1)
    [100, 500, 200, 1]
    
    
    
    """
    
    # ppp2 = _partial(max, 100, _1, 200, _2)
    # ppp2 = _partial(max, 100, _1, 500, _2)
    # ppp = _partial(max, 100, _1, 200, _2, rearg=[3,2,1], curried=True)
    # print(ppp()(0)(300))
    # print(_partialFunctionCreator.cache_info())

    
    
    
def setup(_):

    # Compose Function
    _.mixin({
    
        'memoize': memoize,
        'ARG1': ARG1,
        'ARG2': ARG2,
        'ARG3': ARG3,
        'ARG12': ARG12,
        'ARG13': ARG13,
        'ARG23': ARG23,
        'composeWith': composeWith,
        'composer': _Composer(_),
    })
    
    
    # Partial Function
    _.mixin({
        'escape_name_1': _1,
        'escape_name_2': _2,
        'escape_name_3': _3,
        'escape_name_4': _4,
        'escape_name_5': _5,
        'escape_name_6': _6,
        'spread': spread,
        'rest': rest,
        'overArgs': overArgs,
        'countArgs': countArgs,
        
        'partial': partial,
        'partialRight': partialRight,
        'reverseArgs': flip,        # API Name?
        'curry': curry,
        'uncurry': uncurry,
        'curryRight': curryRight,
        'ary': ary,
        'unary': unary,
        'rearg': rearg,
        'negate': negate,
    })
    
    # Operator Functions
    _.mixin({
        'add': operator.add,
        'sub': operator.sub,
        'div': operator.truediv,
        'mul': operator.mul,
        'mod': operator.mod,
        'neg': operator.neg,
        
        'not_': operator.not_,
        'and_': lambda x, y: x and y,
        'or_': lambda x, y: x and y,
        
        'setitem': operator.setitem,
        'delitem': operator.delitem,
        'getitem': operator.getitem,
        
        'lt': operator.lt,
        'le': operator.le,
        'eq': operator.eq,
        'ne': operator.ne,
        'ge': operator.ge,
        'gt': operator.gt,
    })
    
    
    