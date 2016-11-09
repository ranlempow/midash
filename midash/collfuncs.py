
def resetChain(method):
    def m(self):
        result = method(self)
        self._reset_chain()
        return result
    return m



chainable = {
    'size': False,
    'indexOf': False,
    'equal': False,
}
def _inject_method(klass):
    for k, v in globals().copy().items():
        if k.startswith('a_'):
            k = k[2:]
            setattr(klass, k, klass._create_wrap_method(v, chainable.get(k, True)))
              


class WrapperArray:
    def __init__(self, array):
        self.array = array
        self._reset_chain()
    
    def _reset_chain(self):
        self._chain_iter = self.array
        
    @resetChain
    def copy(self):
        return WrapperArray(list(self._chain_iter))
        
    @resetChain
    def commit(self):
        self.array = list(self._chain_iter)
        return self
        
    @resetChain
    def iter(self):
        new_iter = WrapperArray(self.array)
        new_iter._chain_iter = self._chain_iter
        return new_iter
        
    @resetChain
    def  __iter__(self):   
        return iter(self._chain_iter)
    
    @classmethod
    def _create_wrap_method(cls, method, chain):
        if chain:
            def f(self, *args, **kwargs):    
                self._chain_iter = method(self._chain_iter, *args, **kwargs)
                return self
        else:
            def f(self, *args, **kwargs):    
                result = method(self._chain_iter, *args, **kwargs)
                self._chain_iter = self.array
                return result
        return f
    
_inject_method(WrapperArray)



from collections import namedtuple
              

_asObject = object()
_asArray = object()

class Array(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._map = {}
        self._state = _asObject
        self._reset_chain()
        
        
    def _iter_array(self):
        for i in range(len(self)):
            yield self[i]
            
    def _iter_object(self):
        for k, v in self.__dict__.items():
            if not (isinstance(k, str) and k[0] == '_'):
                yield k, v
        for i, v in enumerate(self._iter_array()):
            yield i, v

            
    def _get_iter(self):
        if self._state is _asObject:
            _iter = self._iter_object() 
        elif self._state is _asArray:
            _iter = self._iter_array()
        return _iter
        
        
    def _reset_chain(self):
        self._chain_iter = self._get_iter()
        self._is_modified_chain = False
        
    def _commit_chain(self):
        if self._is_modified_chain:
            if self._state is _asObject:
                for k in list(self.__dict__.keys()):
                    delattr(self, k)
                for k, v in self._chain_iter:
                    setattr(self, k, v)
            elif self._state is _asArray:
                self[:] = self._chain_iter
            
    def _asSomething(thing):
        def f(self):
            self._commit_chain()
            self._state = thing
            self._reset_chain()
            return self
        return f
    
    asObject = _asSomething(_asObject)
    asArray = _asSomething(_asArray)
    
        
    @resetChain
    def copy(self):
        arr = Array(self._chain_iter)
        arr._state = self._state
        arr._reset_chain()
        return arr
        
    @resetChain
    def commit(self):
        self._commit_chain()
        return self
        
    @resetChain
    def iter(self):
        new_iter = WrapperArray(self)
        new_iter._chain_iter = self._chain_iter
        return new_iter
        
    @resetChain
    def  __iter__(self):
        return self._chain_iter
        
    @classmethod
    def _create_wrap_method(cls, method, chain):
        if chain:
            def f(self, *args, **kwargs):    
                self._chain_iter = method(self._chain_iter, *args, **kwargs)
                return self
        else:
            def f(self, *args, **kwargs):    
                result = method(self._chain_iter, *args, **kwargs)
                self._chain_iter = self
                return result
        return f
    
    def set(self, k, v):
        if isinstance(k, int):
            self[k] = v
        else:
            self.__dict__[k] = v
            
    def get(self, k, default=None):
        if isinstance(k, int):
            return self[k]
        else:
            return self.__dict__[k]
            
    def has(self, k):
        if isinstance(k, int):
            return False
        else:
            return self.__dict__[k]
            
        
_inject_method(Array)



class Chain:
    def __init__(self):
        self._call = _identity
    
    def apply(self, obj):
        return self._call(obj)
    
    @classmethod
    def _create_wrap_method(cls, method, chain):
        def f(self, *args, **kwargs):
            prevcall = self._call
            def f2(obj):
                return method(prevcall(obj), *args, **kwargs)
            self._call = f2
            return self
        return f
        
_inject_method(Chain)
















def _test__():
    def pl(arr):
        print(list(arr))
        
        
    #a = WrapperArray([1,2,3])
    a = Array([1,2,3]).asArray()
    # assert( a.copy().remove(2).union([1,2,3,4]).equal([1,3,2,4]) )
    assert( a.copy().intersection([4,3,2]).equal([2,3]) )
    assert( a.copy().difference([4,3,2]).equal([1]) )
    assert( a.copy().insert(3, 4).insert(0, 0).equal([0,1,2,3,4]) )
    assert( a.copy().extend([2,3,4]).unique().equal([1,2,3,4]) )
    assert( a.copy().extend([0,0,0]).equal([1,2,3,0,0,0]) )
    assert( a.copy().extend([0,0,0]).compact().equal([1,2,3]) )
    assert( a.copy().compress([0,1,1]).equal([2,3]) )
    assert( a.copy().clear().equal([]) )
    #assert( a.copy().extend([8]).commit()[3] == 8)

    b = a.copy()
    ext = b.extend
    ext([8])
    ext([9])
    assert( b.equal([1,2,3,8,9]) )


    b = a.copy()
    it = b.extend([8]).iter()
    it.extend([9])
    assert( it.equal([1,2,3,8,9]) )
    assert( b.equal([1,2,3]) )

    ch = Chain().extend([8]).size()
    assert( ch.apply([1,2,3]) == 4 )
    assert( ch.apply([]) == 1 )

    a.b = 2
    pl( a.asObject() )

