
def attempt(func, *args):
    """
    Attempts to invoke func, 
    returning either the result or the caught error object.
    
    >>> attempt(open, 'not-exist')
    FileNotFoundError(2, 'No such file or directory')
    
    """
    try:
        return func(*args)
    except Exception as e:
        return e
    
    
def forgive(acceptError, func, *args):
    """
    >>> forgive({ FileNotFoundError: 'nofile' }, open, 'not-exist')
    'nofile'
    """
    value = attempt(func, *args)
    if not isinstance(value, Exception):
        return value
    err = value
    for errorClass, default in acceptError.items():
        if isinstance(err, errorClass):
            return default
    raise err
    
def error(message=None):
    raise Exception(message)
    