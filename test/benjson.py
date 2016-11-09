import os
import sys
from benchtool import setup
sys.path.insert(0, os.path.abspath('../midash'))


def setup_objects(number=1000, attrNumber=50):
    import itertools
    import random
    random.seed(0)
    
    chars = [ chr(c) for c in range(ord('a'), ord('z') + 1)]
    def genName():
        return ''.join( random.choice(chars) for i in range(20) )
    def genValue(attrNumber=attrNumber):
        r = random.random()
        if r < 0.2:
            return [{'a'*8: i, 'b'*8: i+1} for i in range(int(r * 100))]
        return r #int(r * 100)
        
    def genObject(attrNumber=attrNumber):
        return dict( (genName(), genValue()) for i in range(attrNumber) )
    return [ genObject() for i in range(number) ], None
    
    
@setup(setup_objects)
def pack_json(objs, _):
    import json
    def run():
        json.dumps(objs)
    return run

@setup(setup_objects)
def pack_umsgpack(objs, _):
    import umsgpack2 as umsgpack
    def run():
        umsgpack.dumps(objs)
    return run
    
@setup(setup_objects)
def pack_msgpack(objs, _):
    import msgpack
    def run():
        msgpack.dumps(objs)
    return run
    
@setup(setup_objects)
def pack_ujson(objs, _):
    import ujson
    def run():
        ujson.dumps(objs)
    return run
    
@setup(setup_objects)
def pack_jsonlua(objs, _):
    import jsonlua
    def run():
        len(jsonlua.dumps(objs))
    return run
    
@setup(setup_objects)
def pack_simplejson(objs, _):
    import simplejson
    def run():
        len(simplejson.dumps(objs))
    return run
    
    
@setup(setup_objects)
def unpack_json(objs, _):
    import json
    data = json.dumps(objs)
    def run():
        json.loads(data)
    return run

@setup(setup_objects)
def unpack_umsgpack(objs, _):
    import umsgpack2 as umsgpack
    data = umsgpack.dumps(objs)
    def run():
        umsgpack.loads(data)
    return run

@setup(setup_objects)
def unpack_msgpack(objs, _):
    import msgpack
    data = msgpack.dumps(objs)
    def run():
        msgpack.loads(data)
    return run
    
    
@setup(setup_objects)
def unpack_ujson(objs, _):
    import ujson
    data = ujson.dumps(objs)
    def run():
        ujson.loads(data)
    return run
    
    
@setup(setup_objects)
def unpack_jsonlua(objs, _):
    import jsonlua
    data = jsonlua.dumps(objs)
    def run():
        jsonlua.loads(data)
    return run
    
    
@setup(setup_objects)
def unpack_simplejson(objs, _):
    import simplejson
    data = simplejson.dumps(objs)
    def run():
        simplejson.loads(data)
    return run
    
    
suit1 = {
    'benchs': [
        pack_jsonlua,
        unpack_jsonlua,
        pack_simplejson,
        unpack_simplejson,
        pack_json,
        unpack_json,
        pack_umsgpack,
        unpack_umsgpack,
        # pack_msgpack,
        # unpack_msgpack,
        pack_ujson,
        # unpack_ujson,
    ],
    'params': [
        (10, 500),
        (100, 50),
        (1000, 5),
    ]
}
