import inspect
import re
import binascii
import types

def g():
    a = 1
    def f(c):
       i = c
       return c + 2
    return f
    return (
        lambda c: c+1
    )
    
def _indentOnHead(body):
    lines = body.split('\n')
    indent = len(lines[0])
    for i, c in enumerate(lines[0]):
        if c != ' ':
            indent = i
            break
    lines = [ln[indent:] for ln in lines]
    return '\n'.join(lines)
        
def serifunc(f):
    if f.__name__ == '<lambda>':
        body = inspect.getsource(f)
        id = 'lambda_' + '%x' % binascii.crc32(body.encode('utf-8'))
        body = re.sub(r'lambda ([^:]*):(.*)', r'def ' + id + r'(\1): return \2', body)
    else:
        body = getattr(f, '_body', None) or inspect.getsource(f)
        id = getattr(f, 'id', (f.__module__ or '') + '.' + f.__qualname__)
        
    assert( '\\' not in body )
    assert( f.__closure__ is None)
    
    obj = {}
    obj['type'] = 'Function'
    obj['id'] = id
    obj['body'] = _indentOnHead(body)
    return obj
    
def desefunc(obj):
    assert( obj['type'] == 'Function' )
    locale_scope = {}
    exec(obj['body'], globals(), locale_scope)
    funcname = obj['id'].rsplit('.', 1) [-1]
    func = locale_scope[funcname]
    func.id = obj['id']
    func._body = obj['body']
    return func
    
sf = serifunc(g())
print(sf)
h = desefunc(sf)
sh = serifunc(h)
print(sh)
print(desefunc(sh)(3))

    
def sericlass(cls):
    obj = {}
    obj['id'] = cls.__name__
    for k, v in cls.__dict__.items():
        if k in ['__weakref__', '__dict__', '__module__', '__doc__']:
            continue
        if isinstance(v, types.FunctionType):
            v = serifunc(v)
        obj[k] = v
    
    return obj
    
class A:
    a = 0
    def foo(self, c):
        return c
        
        
print(sericlass(A))



'''
import ast
print(gln(f))

for node in ast.walk(ast.parse(gln(f))):
    print(node.__dict__)
    
    
def a(v):
    return v
    
def b(v):
    return a(v)
    
def c(v):
    return b(v)
    
assert( 1 == c(b(a(1)) == c(1)) )
'''