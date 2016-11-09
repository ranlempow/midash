from midash import _
_.require('memoize')

@_.memoize
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


def _identity(*v):
    if len(v) == 1:
        return v[0]
    return v


class _PlaceHolder():
    def __init__(self, i):
        self.i = i
        
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

@_.memoize
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
    
    # transfrom to BindArgument
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
    import sys
    _.mixin(sys.modules[__name__])
    _.mixin({
        'escape_name_1': _1,
        'escape_name_2': _2,
        'escape_name_3': _3,
        'escape_name_4': _4,
    })
    
