import inspect
import re
import binascii
import types

class PlaceHolder:
    def __init__(self, func):
        self.func = func
        
    def __call__(self, args, kwargs={}):
        return self.func(*args, **kwargs)
        
class PlaceHolderPick:
    def __init__(self, pos):
        self.pos = pos
    
    def __call__(self, args, kwargs=None):
        return args[self.pos]
    
_1 = PlaceHolderPick(0)
_2 = PlaceHolderPick(1)
_3 = PlaceHolderPick(2)
_4 = PlaceHolderPick(3)

        
class Function:
    def __init__(self, func, param=None, body=None):
        self.func = func
        self.param = param
        self.body = body
        self._closure_args = ()
        self._partial_args = ()
        
    def _body_inline(self, *args, **kwargs):
        body = self.body
        def replace(body, k, v):
            if isinstance(v, Function):
                '''
                f = x -> x + 1
                >>> _body_inline('f, a -> f(a)', f)
                a -> a + 1
                '''
                last = 0
                new_body = ''
                for m in re.finditer(' ' + k + r'\((.*?)\) ', body):
                    param = m.group(1).split(',')
                    new_body += body[last:m.start()]
                    new_body += v._body_inline(*param)[1]
                    last = m.end()
                return new_body + body[last:]
            else:
                return body.replace(' %s ' % k, ' %s ' % v)
            
        i = None
        for i, clos in enumerate(self._closure_args + args):
            body = replace(body, self.param[i], clos)
            
        param = list(self.param[i+1 if i is not None else 0:])
        for k, v in kwargs.items():
            assert(k in param)
            param.remove(k)
            body = replace(body, k, v)
        return ', '.join(param), body
        
    def inline(self, *args, **kwargs):
        param, body = self._body_inline(*args, **kwargs)
        code = 'lambda %s: %s' % (param, body)
        print(code)
        return eval(code)
       
    def _transform(self, args, kwargs):
        if not self._partial_args:
            return args
        elif self._partial_args[-1] == '_placeholder_end':
            return tuple(p(args, kwargs) for p in self._partial_args[:-1]) + args[len(self._partial_args)-1:]
        else:
            return tuple(p(args, kwargs) for p in self._partial_args)
        
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
        
    @property
    def _cached(self):
        inspect.cleandoc('''
        def f(this, func, {0}):
            def f2(*args, kwargs):
                return func({1}, *this._transform(args, kwargs), **kwargs)
            return f2
        ''')
        
    def __call__(self, *args, **kwargs):
        return self.func(*(self._closure_args + self._transform(args, kwargs)), **kwargs)
    
class OverFunction(Function):
    def __init__(self):
        super().__init__(lambda *a: a)
        
    def overMore(self, *funcs):
        return self.partial(map(PlaceHolder, funcs))
        
def over(*funcs):
    return OverFunction().overMore(funcs)


def Lambda(body, **closure):
    assert '->' in body
    param, body = body.split('->')
    param_list = tuple(closure.keys()) + tuple(p.strip() for p in param.split(','))
    complete_param = ', '.join(param_list)
    code = 'lambda %s: %s' % (complete_param, body)
    func = eval(code)
    return Function(func, param_list, body).closure(*closure.values())


a=8
print(Lambda('x -> a + x ', a=a)(3))
print(Lambda('x -> a + x ', a=a).inline(x=4)())
# print(Lambda('y -> y + 5 ')._body_inline(4))
print(Lambda('f -> a + f( a ) ', a=a).inline(f=Lambda('y -> y + y '))())
print(Lambda('f, a -> a + f( a ) ').inline(f=Lambda('y -> y + y '))(2))




    
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

