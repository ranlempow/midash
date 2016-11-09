import json
from collections import OrderedDict
import inspect
import types


class ImmutableError(Exception):
    pass
    
_getattr = object.__getattribute__

class Object(list):
    def __init__(self):
        self.id = id(self)
        self._bounds = []
        self._prototype = None
        
        self._revref_counts = {}
        self._refs = set()
        
    
    def setPrototype(self, proto=None):
        for k in self._bounds:
            delattr(self, k)
        if self._prototype:
            RootStoreSpace.removeInstance(self)
        self._bounds = []
        self._prototype = proto
        if self._prototype:
            RootStoreSpace.addInstance(self)
            for k in dir(proto.__class__):
                method = getattr(proto.__class__, k)
                if k[0] != '_' and callable(method):
                    setattr(self, k, types.MethodType(method, self))
                    self._bounds.append(k)
        else:
            pass
            # TODO: 是不是要unlink all?
        
        
    ## ==================
    ## Ref System
    ## ==================
    
    def __hash__(self):
        return id(self)
    
    def link(self, ref):
        self._refs.add(ref)
        ref._revref_counts[self] = ref._revref_counts.get(self, 0) + 1
        
    def unlink(self, target=None, count=1):
        if target is None:
            # unlink all children
            for ref in list(self._refs):
                self.unlink(ref, count=None)
        else:
            assert target in self._refs
            if count == 1:
                # refcount - 1 
                refcount = target._revref_counts.get(self, 0) - 1
            else:
                # refcount = 0
                refcount = 0
            if refcount <= 0:
                del target._revref_counts[self]
                self._refs.remove(target)
            else:
                target._revref_counts[self] = refcount
                
    def revUnlink(self, revref=None):
        if revref is None:
            # unlink all parent
            for revref in list(self._revref_counts.keys()):
                revref.unlink(target=self, count=None)
        else:
            revref.unlink(target=self, count=None)
        
    def setRef(self, attr, object):
        if isinstance(attr, str):
            op = self.__dict__
            if getattr(object, '_prototype', None) and attr in self.__dict__:
                self.unlink(self.__dict__[attr])
        else:
            op = self
            if getattr(object, '_prototype', None):
                self.unlink(self[attr])
            
        if object is not None:
            op[attr] = object
            if getattr(object, '_prototype', None):
                self.link(object)
        else:
            del op[attr]
        
        
    def destory(self):
        # tall refs: this object is no longer refer it
        self.unlink()
        
        # TODO: 把這個功能做成revUnlink的選項之一
        for revref in self._revref_counts.keys():
            # search list
            while self in revref: revref.remove(self)
            
            # search dict
            removes = [k for k, v in revref.__dict__.items() if v is self]
            for k in removes:
                delattr(revref, k)
                
        # tall refereds: 
        self.revUnlink()
        
        RootStoreSpace.removeInstance(self)
        
    def alter(self):
        # TODO: RootStoreSpace.alterInstance?
        RootStoreSpace._alters.add(self)
        
    # =============
    
    
    def instance(self, _id=None):
        return StoreSpace.instance_object(self, _id=None)
        
        
    def __getattr__(self, name):
        p = object.__getattribute__(self, '_prototype')
        return _getattr(p, name)
        
    def __repr__(self):
        if self._prototype:
            return '<object {} {}>'.format(self._prototype.__class__.__name__, self.id)
        elif list.__len__(self) > 0:
            return str(list(self))
        else:
            return str( dict( (k,v) for k, v in self.__dict__.items() if not (k[0] == '_' or k == 'id')) )
    
class ImmutableObject(Object):
    _immutable = False
    def __init__(self):
        self.__dict__['_immutable'] = False
        Object.__init__(self)
        
    def __setattr__(self, name, val):
        if name in ['_immutable'] or not self._immutable:
            return object.__setattr__(self, name, val)
        raise ImmutableError("Object is Immutable, when set {}".format(name))
        
    def __setitem__(self, key, val):
        raise ImmutableError("Object is Immutable, when index {}".format(key))
        
    def instance(self):
        return self
        
    
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
                obj = _class( (k, self.construct(v)) for k, v in json_value.items())
                self._proto_store.setdefault(_type, {})[obj.id] = obj
                return obj
            else:
                obj = ImmutableObject() if _immutable else Object()
                for k, v in json_value.items():
                    setattr(obj, k, self.construct(v))
                if _immutable: obj._immutable = True
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
            #   prime              -> 參照
            #   prototype          -> 參照
            #   ImmutableObject    -> 參照
            #   objectWithNotProto -> 實體化(新物件)
            #   objectWithProto    -> link
            
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
    
RootStoreSpace = StoreSpace()


    

class PrototypeMetaClass(type):
    def __init__(cls, name, bases, namespace):
        RootStoreSpace.types[name] = cls
        
    def __repr__(cls):
        return "<prototype class %s>" % cls.__name__

    
class Prototype(metaclass=PrototypeMetaClass):
    _immutable = False
    def __init__(self, kwpairs, _id=None):
        _immutable = False
        self.id = _id
        for k, v in kwpairs:
            setattr(self, k, v)
        if not self.id:
            self.id = str(id(self))
        self.freeze()
        
    def freeze(self):
        self._immutable = True
        
    def instance(self, _id=None):
        return StoreSpace.instance_object(self, _id)
        
    def __setattr__(self, name, val):
        if name in ['_immutable'] or not self._immutable:
            return object.__setattr__(self, name, val)
        raise ImmutableError("Prototype is Immutable, when set {}".format(name))

    def __delattr__(self, name):
        raise ImmutableError("Prototype is Immutable, when del {}".format(name))
        
    def __repr__(self):
        return "<prototype %s>" % self.__class__.__name__
        

        
        
        
        
        
class B(Prototype):
    def __init__(self, _dict):
        super().__init__(_dict)
        self._immutable = False
        self.freeze()
        
    #def onLoad(self):
    #    pass
        
    def methodB(self):
        return self.b
        
def test():        
    raw_data = [
        {
            "a": 1,
            "b": 100,
            "map": { "item1": 200},
            "array": [0,1,2,3],
            "type": "B",
        }
    ]
        
    ## ============
    ## test prototype
    ## ============
    
    c_list = RootStoreSpace.fromJson(json.dumps(raw_data))
    c = c_list[0]
    
    assert( isinstance(c, Prototype) )
    assert( isinstance(c, B) )
    assert( str(c.map) == str({"item1": 200}) )
    assert( str(c.array) == str([0,1,2,3]) )
    
    ## ============
    ## test instance
    ## ============
    
    ci = c.instance()
    ci.a += 1
    ci.d = 3
    
    assert( ci.a == 2 )
    assert( ci.d == 3 )
    assert( ci._prototype == c )
    assert( ci.methodB() == ci.b )
    assert( ci.map.item1 == 200 )
    assert( ci.array[2] == 2 )
    # TODO: not allow alter object in prototype
    #ci.map.item1 = 1
    
    
    print(RootStoreSpace._proto_store)
    print(RootStoreSpace._inst_store)
    
    
    ## ============
    ## test ref system
    ## ============
    
    ci1 = c.instance('ci1')
    ci2 = c.instance('ci2')
    ci1.watch = ci2
    ci1.append(ci2)
    ci1.link(ci2)
    
    
    ci1.link(ci2)
    assert( ci2 in ci1._refs )
    assert( ci2._revref_counts[ci1] == 2 )
    
    ## ===========
    ## test changed notify
    ## ===========
    
    ci3 = c.instance('ci3')
    ci2.watch = ci3
    ci2.link(ci3)
    ci3.alter()
    
    changes = RootStoreSpace.getChanges()
    assert( list(changes[ci1]) == [ci2] )
    assert( list(changes[ci2]) == [ci3] )
    
    ## ===========
    ## test destory
    ## ===========
    
    assert(ci1.watch is ci2)
    assert(ci1[0] is ci2)
    ci2.destory()
    assert( not hasattr(ci1, 'watch') )
    assert( len(ci1) == 0 )
    assert( not ci1._refs )
    assert( not ci1._revref_counts )
    
    
    ## ===========
    ## test cycle ref
    ## ===========
    
    ci1.link(ci3)
    ci3.link(ci1)
    ci3.alter()
    changes = RootStoreSpace.getChanges()
    print(changes)
    
    
class NormalObject:
    pass

def bench():
    import timeit
    NUM_1M = 1000 * 1000
    def gen1():
        obj = RootStoreSpace.fromJson('{"a": 0, "b": 100, "type":"B"}')[0]
        #obj.a = 1
        return obj.instance()
        
    def gen2():
        obj = NormalObject()
        obj.a = 1
        return obj
    gen3 = lambda: {'a':1}
    
    print(timeit.timeit('c.a=10', setup='from __main__ import gen2; c=gen2()', number=NUM_1M))
    print(timeit.timeit('a=c.a', setup='from __main__ import gen2; c=gen2()', number=NUM_1M))
    print(timeit.timeit('c["a"]=10', setup='from __main__ import gen3; c=gen3()', number=NUM_1M))
    print(timeit.timeit('a=c["a"]', setup='from __main__ import gen3; c=gen3()', number=NUM_1M))
    print(timeit.timeit('c.a=10', setup='from __main__ import gen1; c=gen1()', number=NUM_1M))
    print(timeit.timeit('a=c.a', setup='from __main__ import gen1; c=gen1()', number=NUM_1M))
        
        
if __name__ == '__main__':
    test()

