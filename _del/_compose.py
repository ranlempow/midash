from midash import _

class _CloseVariable:
    def __init__(self, pos, func_t=None):
        self.func_t = func_t or (lambda x: x)
        self.pos = pos
        
    def __call__(self, t=None):
        return _CloseVariable(self.pos, t)
        
    def transfrom(self, args):
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
                    return wrapper.func(obj, *map(lambda a: a.transfrom(args) if isinstance(a, _CloseVariable) else a, w_args))
            elif                  not wrapper.isNeedTransfrom:
                def f(obj, *args):
                    return wrapper.func(func(obj, *args))
            else:
                def f(obj, *args):
                    return wrapper.func(func(obj, *args), *map(lambda a: a.transfrom(args) if isinstance(a, _CloseVariable) else a, w_args))
            return f
        return functools.reduce(chained, self.chain, None)

def composeWith(module):
    return _Composer(module)
composer = _Composer(_)

# def add_(obj, y):
    # return obj + y
# f = _.add(3).add(4).add(C2(lambda x: bool(x))).compose()

