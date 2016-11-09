

def choose(cond, value, default=None):
    """
    1. use predicate function to test the value. return value when pass test, return default value when fail
    2. if condition is true, value returned
    
    >>> choose(lambda s: s.isdigit(), 'a', '0')
    '0'
    >>> choose(lambda s: s.isdigit(), '1', '0')
    '1'
    >>> choose(callable, 100, int)()
    0
    """
    if callable(cond):
        cond = cond(value)
    return value if cond else default
    
def defaultTo(value, defaultValue):
    """
    Checks value to determine whether a default value should be returned in its place.
    The defaultValue is returned if value is NaN, None, nil.
    """
    if value is None or value == float('NaN'):
        return defaultValue
    return value
    
    
def constant(value):
    """
    Creates a function that returns value.
    
    >>> constant(7)()
    7
    """

    return lambda: value


def random(lower, upper=None):
    """
    random([lower=0], upper)
    Produces a random number between the inclusive lower and upper bounds.
    If upper is not specified, it's set to lower with lower then set to 0.
    If only one argument is provided a number between 0 and the given number is returned.
    """
    import random
    r = random.random()
    if upper is None:
        upper = lower
        lower = 0
    
    if isinstance(upper, int):
        delta = upper - lower + 1
        value = r * delta + lower
        return ceil(value)
    else:
        return r * (upper - lower) + lower
        

def inRange(number, start, end=None):
    """
    inRange(number, [start=0], end)
    Checks if n is between start and up to, but not including, end.
    If end is not specified, it's set to start with start then set to 0.
    If start is greater than end the params are swapped to support negative ranges.
    
    >>> inRange(0, 2), inRange(1, 2), inRange(2, 2)
    (True, True, False)
    >>> inRange(0, -2), inRange(-1, -2), inRange(2, -2)
    (True, True, False)
    
    """
    if end is None:
        end = start
        start = 0
    if start < end:
        return start <= number < end
    else:
        return end < number <= start



def clamp(number, lower, upper=None):
    """
    clamp(number, [lower=0], upper)
    Clamps number within the inclusive lower and upper bounds.
    
    >>> clamp(-10, -5, 5), clamp(10, -5, 5)
    (-5, 5)
    """
    if upper is None:
        upper = lower
        lower = 0
    return min(max(lower, number), upper)

