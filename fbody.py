import inspect
import re
import binascii
import types
import copy

class PlaceHolder:
    def __init__(self, func):
        self.func = func
        
    def apply(self, args, kwargs={}):
        return self.func(*args, **kwargs)

class PlaceHolderConst:
    def __init__(self, value):
        self.value = value
        
    def apply(self, args, kwargs=None):
        return self.value
        
class PlaceHolderApply:
    def __init__(self, poses, func=None):
        self.poses = poses
        self.func = func
    
    def apply(self, args, kwargs={}):
        return self.func(*map(lambda i: args[i], self.poses))
    
    def __call__(self, func):
        return PlaceHolderApply(self.poses, func)
        
class PlaceHolderPick:
    def __init__(self, pos):
        self.pos = pos
    
    def apply(self, args, kwargs=None):
        return args[self.pos]
    
    def __call__(self, func):
        return PlaceHolderApply([self.pos], func)
    
    
_1 = PlaceHolderPick(0)
_2 = PlaceHolderPick(1)
_3 = PlaceHolderPick(2)
_4 = PlaceHolderPick(3)

_12 = PlaceHolderApply((1, 2))
_13 = PlaceHolderApply((1, 3))
_23 = PlaceHolderApply((2, 3))
_14 = PlaceHolderApply((1, 2))
_24 = PlaceHolderApply((2, 4))
_34 = PlaceHolderApply((3, 4))


  
  
class Function:
    def __init__(self, func, param=None, body=None):
        self.func = func
        self.param = param
        self.body = body
        self._closure_args = ()
        self._partial_args = ()
        
       
    def _transform(self, args, kwargs):
        if not self._partial_args:
            return args
        elif self._partial_args[-1] == '_placeholder_end':
            return tuple(p.apply(args, kwargs) for p in self._partial_args[:-1]) + args[len(self._partial_args)-1:]
        else:
            return tuple(p.apply(args, kwargs) for p in self._partial_args)
        
    def closure(self, *closure_args):
        self._closure_args += closure_args
        return self
     
    def partial(self, *partial_args):
        self._partial_args = partial_args
        return self
        
    # def applyFlow(self, func, *compose_args):
        # self._partial_args = (PlaceHolderChain(func),) + compose_args
        # return self
        
    def applyCompose(self, func, *compose_args):
        fobj = Function(func)
        fobj.partial(PlaceHolder(self), *compose_args)
        return fobj
        
    def __call__(self, *args, **kwargs):
        return self.func(*(self._closure_args + self._transform(args, kwargs)), **kwargs)
    
class OverFunction(Function):
    def __init__(self):
        super().__init__(lambda *a: a)
        
    def overMore(self, *funcs):
        return self.partial(map(PlaceHolder, funcs))
        
def over(*funcs):
    return OverFunction().overMore(funcs)


def lambda_(body, **closure):
    assert '->' in body
    param, body = body.split('->')
    param_list = tuple(closure.keys()) + tuple(p.strip() for p in param.split(','))
    complete_param = ', '.join(param_list)
    code = 'lambda %s: %s' % (complete_param, body)
    func = eval(code)
    return Function(func, param_list, body).closure(*closure.values())







a=8
print(lambda_('x -> a + x ', a=a)(3))






def g():
    a = 1
    def f(a, c):
       i = a
       return c + i
    f = Function(f).closure(a)
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
    closure = None
    if isinstance(f, Function):
        id = f.func.__name__
        body = getattr(f.func, '_body', None) or inspect.getsource(f.func)
        closure = f._closure_args
    elif isinstance(f, types.BuiltinFunctionType):
        id = f.__name__
        body = '<builtin>'
    elif f.__name__ == '<lambda>':
        body = inspect.getsource(f)
        id = 'lambda_' + '%x' % binascii.crc32(body.encode('utf-8'))
        body = re.sub(r'lambda ([^:]*):(.*)', r'def ' + id + r'(\1): return \2', body)
    else:
        body = getattr(f, '_body', None) or inspect.getsource(f)
        id = getattr(f, 'id', (f.__module__ or '') + '.' + f.__qualname__)
        
    assert( '\\' not in body )
    assert( not hasattr(f, '__closure__') or f.__closure__ is None)
    
    
    obj = {}
    obj['type'] = 'Function'
    obj['id'] = id
    obj['body'] = _indentOnHead(body)
    if closure:
        obj['closure'] = closure
    return obj
    
def desefunc(obj):
    import builtins
    assert( obj['type'] == 'Function' )
    if obj['body'] == '<builtin>':
        return builtins.__dict__[obj['id']]
        
    locale_scope = {}
    global_scope = {}
    exec(obj['body'], global_scope, locale_scope)
    print(locale_scope)
    funcname = obj['id'].rsplit('.', 1) [-1]
    func = locale_scope[funcname]
    func.id = obj['id']
    func._body = obj['body']
    if 'closure' in obj:
        func = Function(func).closure(*obj['closure'])
        
    return func
    
    

sf = serifunc(g())
print(sf)
h = desefunc(sf)
sh = serifunc(h)
print(sh)
print(desefunc(sh)(3))


# print(serifunc(g()))
# print(desefunc(serifunc(g())))
    
    
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

