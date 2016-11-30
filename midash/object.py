import types
import json


class NULL:
    pass
    
_null_ = NULL()

'''
aaa
'''
"aa\naaa{dd}"
r"[10]+e\n(?P<e>ee)"


class StoreSpace:
    
    def __init__(self, parent=None):
        self.parent = parent
        self.types = {}
        self._proto_store = {}
        self._inst_store = {}
        
        self._alters = set()
        self._destoryeds = set()
        
    def getChanges(self):
        subChanges = {}
        buffer = self._alters
        while buffer:
            new_buffer = set()
            for alted in buffer:
                for revref in alted._revref_counts.keys():
                    if revref not in subChanges:
                        subChanges[revref] = set()
                        new_buffer.add(revref)
                    subChanges[revref].add(alted)

            buffer = new_buffer
        self._alters = set()
        return subChanges
        
            
    def getType(self, typename):
        return self.types.get(typename, self.parent.getType(typename) if self.parent else None)
    
    def getPrototype(self, type, id, _inst=False):
        store = self._inst_store if _inst else self._proto_store
        try:
            collection = store[type.__class__.__name__]
            return collection[id]
        except KeyError:
            if self.parent:
                return self.parent.getPrototype(type, id)
            raise
            
    def getInstance(self, type, id):
        return self.getPrototype(type, id, _inst=True)
        
    def addInstance(self, object):
        self._inst_store.setdefault(object._prototype.__class__.__name__, {})[object.id] = object
        
    def removeInstance(self, object):
        del self._inst_store[object._prototype.__class__.__name__][object.id]
     
    def fromJson(self, string):
        objects = json.loads(string, object_pairs_hook=self.object_pairs_hook)
        return objects
        
    def toJson(self):
        pass
    

    # TODO: 分為 1.建造成prototype  2.建造成object
    def construct(self, json_value):
        if isinstance(json_value, Object):
            return json_value
        elif isinstance(json_value, list):
            obj = ImmutableObject()
            for v in json_value:
                obj.append(self.construct(v))
            obj._immutable = True
            return obj
        elif isinstance(json_value, OrderedDict):
            _type = json_value.get('type')
            _immutable = json_value.get('immutable', True)
            if _type == 'ref':
                reftype = json_value.get('reftype')
                refid = json_value.get('refid')
                return self.getPrototype(reftype, refid)
            elif _type:
                # all keys must be string (this is always true for json)
                # assert(all( isinstance(k, str) for k in json_value.keys() ))
                _class = self.getType(_type)
                obj = _class((k, self.construct(v)) for k, v in json_value.items())
                self._proto_store.setdefault(_type, {})[obj.id] = obj
                return obj
            else:
                obj = ImmutableObject() if _immutable else Object()
                for k, v in json_value.items():
                    setattr(obj, k, self.construct(v))
                if _immutable:
                    obj._immutable = True
                return obj
        return json_value
        
    
    def object_pairs_hook(self, kwpairs):
        return self.construct(OrderedDict(kwpairs))
        
        
    @classmethod
    def instance_object(cls, source, _id=None):
        obj = Object()
        if _id:
            obj.id = _id
        if isinstance(source, Prototype):
            obj.setPrototype(source)
        elif source._prototype:
            obj.setPrototype(source._prototype)
        
        
        def subinstance(v):
            # 處理子物件
            #   prime              ->參照
            #   prototype          ->參照
            #   ImmutableObject    ->參照
            #   objectWithNotProto ->實體化(新物件)
            #   objectWithProto    ->link
            
            if isinstance(v, Object):
                if v._prototype:
                    obj.link(v)
                else:
                    v = v.instance()
            return v
        
        
        # 把所有子物件都實體化
        for k, v in source.__dict__.items():
            if k == 'id':
                continue
            setattr(obj, k, subinstance(v))
            
        if isinstance(source, list):
            for i, v in enumerate(source):
                obj[i] = subinstance(v)
        return obj
        
        
        
        
        
        
        
        
        
        
        
class StoreSpace:
    def __init__(self, parent=None):
        #self.parent = parent
        #self.types = {}
        #self._proto_store = {}
        #self._inst_store = {}
        self.clearChanges()
        
    def clearChanges(self):
        self.diffs = {}
        self.refs = {}
        
        self._mutations = set()
        self._destoryeds = set()
        self._subchanges = set()
        
    def propagateChanges(self):
        _subchanges = set()
        self._mutations = set(k for k, v in self.diffs.items() if not v)
        buffer = self._mutations
        while buffer:
            new_buffer = set()
            for alted in buffer:
                if hasattr(alted, '_refs'):
                    for referee, count in alted._refs.items():
                        if referee not in _subchanges and count > 0:
                            _subchanges[referee] = set()
                            new_buffer.add(referee)
                        _subchanges[referee].add(alted)

            buffer = new_buffer
        self._subchanges = _subchanges
        
global_space = StoreSpace()


def _common_setattr(self, idx, value, prev=_null_):
    indexer = self._indexer
    space = self._space
    try:
        prev = indexer[idx]
    except KeyError:
        pass
    indexer[idx] = value
    
    # the diff system and the mutation syetem
    if idx not in space.diffs[self]:
        space.diffs[self][idx] = prev
    
    # the referee system
    if prev in space.refs:
        space.refs[prev][self] -= 1
    if value in space.refs:
        space.refs[value][self] = space.refs[value].get(self, 0) + 1
    
    
    
def _common_delattr(self, idx):
    indexer = self._indexer
    space = self._space
    prev = indexer[idx]
    del indexer[idx]
    
    # the diff system and the mutation syetem
    if idx not in space.diffs[self]:
        space.diffs[self][idx] = prev

    # the referee system
    if prev in space.refs:
        space.refs[prev][self] -= 1


def setdefault(self, idx, default):
    if self.has(idx):
        return self.get(idx)
    else:
        self.set(idx, default)
        return default


def destory(self):
    space = self._space
    
    # refer system
    # --------------
    # tall refs: this object is no longer refer it
    for obj in self._everyItems():
        if obj in space.refs:
            if self in space.refs[obj]:
                del space.refs[obj][self]
    
    # referee system
    if self in space.refs:
        for referee in space.refs[self].keys():
            referee.unlinkAll(self)
    
    space._destoryeds.add(self)
    self.finalize()


def _iter_prototype_methods(proto):
    for k in dir(proto.__class__):
        method = getattr(proto.__class__, k)
        if k[0] != '_' and callable(method):
            yield k, method


def resetPrototype(obj, proto=None):
    space = obj._space
    
    if obj._prototype:
        space.removeInstance(obj)
        for name, method in _iter_prototype_methods(obj._prototype):
            delattr(obj, name)
    
    obj._prototype = proto
    if obj._prototype:
        space.addInstance(obj)
        for name, method in _iter_prototype_methods(obj._prototype):
            setattr(obj, name, types.MethodType(method, obj))
    else:
        pass
        # TODO: ¬O¤£¬O­nunlink all?


def isInstanceOf(obj, proto):
    assert(proto is not None)
    return obj._prototype is proto
    
    
def instance(obj, _id=None):
    space = obj._space
    return space.instance_object(obj, _id=_id)
    

def _reset_chain(self):
    old_chainiter = self._chain_iter
    self._chain_iter = self._inner_iter()
    self._is_modified_chain = False
    return old_chainiter


@classmethod
def _mixfix(cls, method, chain):
    if chain:
        def f(self, *args, **kwargs):
            self._chain_iter = method(self._chain_iter, *args, **kwargs)
            return self
    else:
        def f(self, *args, **kwargs):
            result = method(self._chain_iter, *args, **kwargs)
            self._reset_chain()
            return result
    return f
    
    
class Object:
    def __init__(self):
        _dict = self.__dict__
        
        _dict['id'] = id(self)
        _dict['_space'] = global_space
        _dict['_indexer'] = _dict
        _dict['_prototype'] = None
        
        # diff system
        self._space.diffs[self] = {}
        
        # refered system (destory function)
        self._space.refs[self] = {}
        
        
    # chainIter system
    # ---------
    
    def _inner_iter(self):
        return self.__dict__.items()
        
    def __iter__(self):
        return self._reset_chain()
        
    def commit(self):
        if self._is_modified_chain:
            chainiter = self._reset_chain()
            for k in list(self.__dict__.keys()):
                delattr(self, k)
            for k, v in chainiter:
                setattr(self, k, v)
        return self
        
    # prototype and object
    # --------------------
        
    def __getattr__(self, name):
        p = object.__getattribute__(self, '_prototype')
        return _getattr(p, name)
        
    def init(self):
        pass
        
    def finalize(self):
        pass
    
    
        
    # refered system
    # --------------
    
    def unlinkAll(self, obj):
        for k, v in self.__dict__.items():
            if obj == k or obj == v:
                self.__delattr__(k)

    def _everyItems(self):
        for k, v in self.__dict__.items():
            yield k
            yield v
            
            
            
    def has(self, idx):
        return idx in self.__dict__
    
    def set(self, idx, value):
        self.__setattr__(self, idx, value)
        
    def get(self, idx, default=None):
        try:
            return self.__getattr__(idx)
        except AttributeError:
            return default
            
    
    
            
class Array(list):
    def __init__(self):
        self._space = global_space
        self._indexer = self
        
        # diff system
        self._space.diffs[self] = {}
        
        # refered system (destory function)
        self._space.refs[self] = {}
        
    # chainIter system
    # ---------
    
    def _inner_iter(self):
        return self.__iter__()
        
    def __iter__(self):
        return self._reset_chain()
        
    def commit(self):
        if self._is_modified_chain:
            chainiter = self._reset_chain()
            self[:] = chainiter
        return self
        
                
    def unlinkAll(self, obj):
        for k, v in enumerate(self):
            if obj == v:
                self.__delitem__(k)
        
    def _everyItems(self):
        return self
        
    def has(self, idx):
        return 0 <= idx < len(self)
    
    def set(self, idx, value):
        self.__setitem__(self, idx, value)
        
    def get(self, idx, default=None):
        try:
            return self[idx]
        except AttributeError:
            return default
            

class Prototype(Object):
    _immutable = False
    
    def freeze(self):
        self._immutable = True
        
    def __setattr__(self, name, val):
        if name in ['_immutable'] or not self._immutable:
            return object.__setattr__(self, name, val)
        raise ImmutableError("Prototype is Immutable, when set {}".format(name))

    def __delattr__(self, name):
        raise ImmutableError("Prototype is Immutable, when del {}".format(name))
    
        
Object.__setattr__ = _common_setattr
Object.__delattr__ = _common_delattr
Object.destory = destory
Object.setdefault = setdefault

Array.__setitem__ = _common_setattr
Array.__delitem__ = _common_delattr
Array.destory = destory
Array.setdefault = setdefault

Object.resetPrototype = resetPrototype
Object.isInstanceOf = isInstanceOf
Object.instance = instance
