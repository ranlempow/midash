from midash import _
_.localize()
_.require('lambda')
_.require('lang')

import sys as _sys
composer = composeWith(_sys.modules[__name__])
MAXSIZE = _sys.maxsize

def _createArrayTriple(array):
    i = 0
    for v in array:
        yield v, i, None
        i += 1

def _createObjectTriple(obj):
    for k, v in obj.items():
        yield v, k, None
        
def triplize(obj):
    """
    >>> list(triplize([10, 20]))
    [(10, 0, None), (20, 1, None)]
    
    >>> list(triplize(triplize([10, 20])))
    [(10, 0, None), (20, 1, None)]
    
    >>> list(sorted(triplize({5:10, 6:20})))
    [(10, 5, None), (20, 6, None)]
    """
    if hasattr(obj, '__next__') or hasattr(obj, 'next'):
        return obj
    #elif isinstance(obj, Array):
    #    return obj.iter()
    elif isinstance(obj, (list, tuple)):
        return _createArrayTriple(obj)
    elif isinstance(obj, dict):
        return _createObjectTriple(obj)
        
        
def wrapperIterTriplize(func, iterPosInArgs):
    def wrap(obj, *args):
        return func(triplize(obj), *args)
    return wrap


def _alwaysIterOnVariableArgs(args, do_triplize=False):
    """
    >>> tuple(_alwaysIterOnVariableArgs( ((1,2),(3,)) ))
    ((1, 2), (3,))
    
    >>> tuple(_alwaysIterOnVariableArgs( ((1,2,3),) ))
    (1, 2, 3)
    
    >>> tuple(_alwaysIterOnVariableArgs( (iter([1,2,3]),) ))
    (1, 2, 3)
    
    >>> tuple(_alwaysIterOnVariableArgs( (1,2,3) ))
    (1, 2, 3)
    
    >>> tuple(_alwaysIterOnVariableArgs( (1,) ))
    (1,)
    >>> tuple(_alwaysIterOnVariableArgs( () ))
    ()
    """
    if not args: return iter(())
    if len(args) == 1:
        if hasattr(args[0], '__next__'):
            return args[0]
        elif hasattr(args[0], '__iter__'):
            return iter(args[0])
    if do_triplize:
        return triplize(args)
    else:
        return iter(args)



isContainor_ = lambda obj: hasattr(obj, '__next__') or hasattr(obj, '__iter__') or hasattr(obj, 'items')

def _equalsBase(obj, other, deeply):
    # TODO: unordered dict
    if not isContainor_(obj) and not isContainor_(other):
        return obj == other
    obj, other = iter(obj), iter(other)
    while(1):
        l_value = next(obj, none)
        r_value = next(other, none)
        if       deeply and not _equalsBase(l_value, r_value, deeply):
            return False
        elif not deeply and not l_value == r_value:
            return False
        if l_value is none or r_value is none:
            return True

equals     = lambda obj, other: _equalsBase(obj, other, False)
equalsDeep = lambda obj, other: _equalsBase(obj, other, True)

equals.__doc__ = """
    >>> equals([0], [0]), equals(0, 0), equals(object(), object())
    (True, True, False)
"""

equalsDeep.__doc__ = """
    >>> equalsDeep([[0], [1]], [[0], [1]])
    True
"""


 
def _zipBase(firstIsTriple=True):
    """
    >>> list(_zipBase()([10, 20], [100, 200]))
    [((10, 100), 0, None), ((20, 200), 1, None)]
    """
    def _doZip(*objs):
        if firstIsTriple:
            firstIter = triplize(objs[0])
            iters = [iter(o) for o in objs[1:]]
        else:
            iters = [iter(o) for o in objs]
        pool = [None for o in objs]
        try:
            while(1):
                if firstIsTriple:
                    pool[0], k, t = next(firstIter)
                    for i, it in enumerate(iters):
                        pool[i+1] = next(it)
                    yield tuple(pool), k, t
                else:
                    for i, it in enumerate(iters):
                        pool[i] = next(it)
                    yield tuple(pool)
        except StopIteration:
            return
    return _doZip
    
zip = _zipBase(firstIsTriple=False)


'''
def a_unzip(obj_iterator):
    obj_iterator = list(obj_iterator)
    maxitems = max(len(obj) for obj in obj_iterator)
    pools = [[] for i in range(maxitems)]
    for obj in obj_iterator:
        for i, pool in enumerate(pools):
            v = None
            if i < len(obj):
                v = obj[i]
            pool.append(v)
    return pools
'''

def concat(*objs):
    for it in _alwaysIterOnVariableArgs(objs):
        for element in it:
            yield element

flatten = concat      # TODO: unary(concat_)
#print(list( flatten_([[1], [2,3]]) ))


identity = lambda v: v
constant = lambda v: lambda _: v
get1     = lambda t: t[1]
get2     = lambda t: t[2]
def bypass(func):
    def f(v):
        func(v)
        return v
    return f
bypass1  = lambda f: lambda t: (t[0], f(t[1]))
bypass2  = lambda f: lambda t: (f(t[0]), t[1])

_map = map
def _map(iteratee, obj):
    for v in obj:
        yield iteratee(obj)
        
def map(obj, iteratee): return _map(iteratee, obj)
keys       = composer.map(get1)()
values     = composer.map(get2)()
forEach    = composer.map(ARG1(lambda f: bypass(f) ))()
mapKeys    = composer.map(ARG1(lambda f: bypass2(f) ))()
mapValues  = composer.map(ARG1(lambda f: bypass1(f) ))()
fill       = composer.map(ARG1(lambda v: constant(v) ))()
fillValues = composer.map(ARG1(lambda v: bypass1(identity)) )()



import functools as _functools
_reduce = _functools.reduce
def reduce(obj, f, m): return _reduce(f, obj, m)

reduceKey = composer.keys().reduce(ARG1, ARG2)()      #  reduceKey_(f, m)
every     = composer.reduce(and_, True)()
some   = composer.reduce(or_, False)()
min    = composer.reduce(min)()
max    = composer.reduce(max)()
sum    = composer.reduce(add, 0)()
size   = composer.fill(1).reduce(add, 0)()
empty  = lambda obj: size_(obj) == 0           # TODO: use first

    

def filter(obj, predicate):  return filter(predicate, obj)
filterKey = composer.filter(ARG1(lambda p: lambda v,k,*_: p(k)))
reject    = composer.filter(ARG1(lambda p: lambda v,*_: not p(v)))
compact   = composer.filter(lambda v,*_: bool(v))
pick      = composer.filterKey(ARG1(lambda vs: lambda k:     has_(vs,k)))
omit      = composer.filterKey(ARG1(lambda vs: lambda k: not has_(vs,k)))
withThe   = composer.filter(ARG1(lambda vs: lambda v,*_: find_(vs,v,none) != none))
without   = composer.filter(ARG1(lambda vs: lambda v,*_: find_(vs,v,none) == none))




    
    

def _extract1(tup): return tup[0] if isinstance(tup, tuple) else tup
#def a_unique(obj, key=None):
def uniqueValue(obj):
    # TODO: keyfunc?
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    seen = set()
    contains = seen.__contains__
    for element in reject_(obj, lambda v, *_: contains(v)):
        seen.add(_extract1(element))
        yield element
        
    
def sliceWith(obj, dropPredicate, retainPredicate):
    newi = 0
    element = next(obj, none)
    
    # erase elements
    while element != none and dropPredicate(*element):
        element = next(obj, none)
        
    # retain elements
    while element != none and retainPredicate(*element):
        yield element[0], newi, element[2]
        element = next(obj, none)
        newi += 1
        
    
    
def slice(obj, begin=None, end=None, step=None):
    # islice('ABCDEFG', 2) --> A B
    # islice('ABCDEFG', 2, 4) --> C D
    # islice('ABCDEFG', 2, None) --> C D E F G
    # islice('ABCDEFG', 0, None, 2) --> A C E G
    it = iter(range(begin or 0, end or MAXSIZE, step or 1))
    
    nexti = next(it, none)
    if nexti == none:
        return
        
    newi = 0
    for v, i, _ in obj:
        if i == nexti:
            yield v, newi, _
            nexti = next(it)
            newi += 1
    
    
def _spliceWithAcceptIter(obj, retainPredicate, dropPredicate, values):
    newi = 0
    element = next(obj, none)
    
    # retain elements
    while element != none and retainPredicate(*element):
        yield element[0], newi, element[2]
        element = next(obj, none)
        newi += 1
        
    # erase elements
    while element != none and dropPredicate(*element):
        element = next(obj, none)
        
    # insert elements
    # TODO: none while
    if values:
        for v in values:
            yield v[0], newi, v[2]
            newi += 1
    
    # yield remainder elements
    while element != none:
        yield element[0], newi, element[2]
        element = next(obj, none)
        newi += 1
        
def spliceWith(obj, retainPredicate, dropPredicate, *values):
    #values = values[0] if values and hasattr(values[0], '__next__') else triplize(values)
    values = _alwaysIterOnVariableArgs(values, do_triplize=True)
    return _spliceWithAcceptIter(obj, retainPredicate, dropPredicate, values)
        
def _spliceAcceptIter(obj, start, n, values):
    start = start     if start >= 0 else MAXSIZE    # erase pos
    stop  = start + n if n >= 0     else MAXSIZE    # insert pos
    return _spliceWithAcceptIter(obj, (lambda v,i,*_: i < start), (lambda v,i,*_: i < stop), values)

def splice(obj, start, n, *values):
    #values = values[0] if values and hasattr(values[0], '__next__') else triplize(values)
    values = _alwaysIterOnVariableArgs(values, do_triplize=True)
    return _spliceAcceptIter(obj, start, n, values)
    


                
                

reverse = reversed
# spliceBy
# sliceBy
# splice(b, e, vs) ->        spliceBy(i < b, i < e, vs)
# slice(b, e)  ->           sliceBy(i < b, i < e)
head       =           composer.slice(0, 1)()
last       = composer.reverse().slice(0, 1)()
initial    = composer.reverse().slice(1, None)()
tail       =           composer.slice(1, None)()
nth        =           composer.slice(ARG1(lambda n: n), ARG1(lambda n: n+1))()
take       =           composer.slice(0, ARG1(lambda n: n))()
takeRight  = composer.reverse().slice(0, ARG1(lambda n: n))()
drop       =           composer.slice(ARG1(lambda n: n), None)()
dropRight  = composer.reverse().slice(ARG1(lambda n: n), None)()


# print('---------')
# print(list( splice(triplize([1,2,3,4]), 0, 0, 9) ))

def extend_(obj, values):      return splice(obj, -1, 0, values)
def clear_(obj):               return splice(obj, 0, -1)
def insert_(obj, idx, value):  return splice(obj, idx, 0, value)
def removeAt_(obj, idx):  return splice(obj, idx, 0)
# def a_remove(obj, value):       return a_splice(obj, a_indexOf(obj, value), 1)

def a_union(*objs): return a_unique(a_concat(*objs))
def a_intersection(obj, other): return a_unique(a_within(obj, *other))
def a_difference(obj, other): return a_unique(a_without(obj, *other))







        
count     = composer.filter(ARG1(lambda v: lambda: value == v)).size()()
find      = composer.filter(ARG1()).head()
# findLast(p)  -> reverse().filter(p).head()
# findKey(p)   -> filter(v,k->p(k)).head()
# findLastKey(p) -> reverse().filter(v,k->p(k)).head()
# contains(v)  -> find(v) != nil
# superset(vs) ->     intersection(vs).len() > 0
# disjoint()   -> not intersection(vs).len() == vs.len()

# indexOf(v)     -> findKey(equals(v))
# lastIndexOf(v) -> findLastKey(equals(v))


def range(start, end, step):
    i = 0
    count = start
    while count < end:
        yield count, i, None
        count += step
        i += 1
    
    
def cycle(iterable):
    # cycle('ABCD') --> A B C D A B C D A B C D ...
    saved = []
    for element in iterable:
        yield element
        saved.append(element)
    while saved:
        for element in saved:
              yield element


def product(*args, repeat=1):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = [tuple(pool) for pool in args] * repeat
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)
        
def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    for indices in product(range(n), repeat=r):
        if len(set(indices)) == r:
            yield tuple(pool[i] for i in indices)

def combinations(iterable, r, replacement=False):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    # combinations('ABC', 2, replacement=True) --> AA AB AC BB BC CC
    generator = product if replacement else permutations
    pool = tuple(iterable)
    n = len(pool)
    for indices in generator(range(n), r):
        if sorted(indices) == list(indices):
            yield tuple(pool[i] for i in indices)
            
