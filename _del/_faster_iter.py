
none = object()
# TODO: remove this function
def _alwaysIterOnVariableArgs(args, do_triplize=False):

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


def spliceF(obj, start, n, *values):
    start = start     if start >= 0 else MAXSIZE    # erase pos
    stop  = start + n if n >= 0     else MAXSIZE    # insert pos
    values = _alwaysIterOnVariableArgs(values, do_triplize=True)
    
    newi = 0
    element = none
    for v, k, t in obj:
        if k < start:
            # retain elements
            yield v, newi, t
            newi += 1
        elif k < stop:
            # erase elements
            pass
        else:
            element = v, k, t
            break
            
    # insert elements
    # TODO: none while
    for v in values:
        yield v[0], newi, v[2]
        newi += 1
    
    # yield remainder elements
    if element != none:
        yield element[0], newi, element[1]
        newi += 1
        for v, k, t in obj:
            yield v, newi, t
            newi += 1
            
def splice_nt(obj, start, n, *values):
    start = start     if start >= 0 else MAXSIZE    # erase pos
    stop  = start + n if n >= 0     else MAXSIZE    # insert pos
    values = _alwaysIterOnVariableArgs(values, do_triplize=False)
    
    element = none
    for k, v in enumerate(obj):
        if k < start:
            # retain elements
            yield v
        elif k < stop:
            # erase elements
            pass
        else:
            element = v
            break
            
    # insert elements
    for v in values:
        yield v
    
    # yield remainder elements
    if element != none:
        yield element
        for v in obj:
            yield v
            
def insertF(obj, idx, value):    return spliceF(obj, idx, 0, value)
def insert_nt(obj, idx, value):  return splice_nt(obj, idx, 0, value)

def range_nt(start, end, step):
    count = start
    while count < end:
        yield count
        count += step
        