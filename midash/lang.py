# -*- coding: UTF-8 -*-

"""
Method Of Builtin Types
-----------------------

| function signature            | description                     |
|-------------------------------|---------------------------------|
| castTo(v, type)               |
| cast(type, v)                 | 型別轉換
| clone(v)                      | 完整複製
| TYPE()                        | 物件建造
| TYPE(v)                       | 物件包覆 or 型別轉換 or 原型替換
| isType(v, type)               |
| is(type, v)                   | 型別判定
| isSubclass(type1, type2)      | 繼承關係判定
| isSuperclass(type1, type2)    |
| typeof(v)                     | 取得物件的型別


### infinity and not-a-number
TODO: this part will move to `math`

"""

import os.path as _path
import sys as _sys
_sys.path.insert(0, _path.abspath(_path.dirname(__file__)))


from midash import _

none = _.Type('none', (), {"__new__": lambda cls, obj=None: cls._default})
none._default = none
none.__doc__ = """
    type of nullity value
    
    functions should not return none, this value is not default value of returning
"""

true = True
""" truth symbol """
false = False
""" false symbol """


def nullity(value):
    """
    null is a value of undefined variable or variable with no initial value
    null is a value of function with no return value
    
    The following values are considered null:
    
    1. None (python)
    2. nil (lua)
    3. _.none
    4. false
    
    example:
    
    >>> nullity(None), nullity(none), nullity(false), nullity(true)
    (False, False, False, True)
    
    >>> not_null_values = [0, 1, -1, 1.0, '', 'a', True]
    >>> all(map(nullity, not_null_values))
    True
    
    """
    return not( (value is None) or (value is none) or (value is False) )
    

@_.mixinTo([_, 'Type'])
def construct(type, value=None):
    """
    create new object of `type`, if `value` is not given, empty value of that type is returned.
    >>> int(), float(), string(), boolean(), none()
    (0, 0.0, '', False, <class none>)
    >>> int.construct(12)
    12
    
    special construct
    >>> float('inf'), -float('inf'), float('nan')
    (inf, -inf, nan)
    
    """
    return type() if value is None else type(value)
    
_py_typeOf = type
_py_toInt = int
_py_toFloat = float
_py_toString = str
_py_toBoolean = bool

_cast_to = lambda cls, obj=None: cls._realType(obj if obj is not None else cls._default)

def _cast_to_string(__type, v=none):
    if v is None:
        return 'nil'
    if is_(boolean, v):
        return 'true' if v else 'false'
    if is_(none, v):
        return ''
        
    # python default cast
    return _py_toString(v)
    
def _cast_to_boolean(__type, v=none):
    if v is none:
        return False
        
    # python default cast
    return _py_toBoolean(v)

int     = _.Type('int',     (), {"__new__": _cast_to, '_realType': _py_toInt, '_default': 0})
int.construct = lambda v=None: construct(int, v)
int.__doc__ = """
    type of integer number
"""
float   = _.Type('float',   (), {"__new__": _cast_to, '_realType': _py_toFloat, '_default': 0.0})
float.construct = lambda v=None: construct(float, v)
float.__doc__ = """
    type of float-point number
"""
string  = _.Type('string',  (), {"__new__": _cast_to_string, '_realType': _py_toString, '_default': ""})
string.construct = lambda v=None: construct(string, v)
string.__doc__ = """
    type of string
"""
boolean = _.Type('boolean', (), {"__new__": _cast_to_boolean, '_realType': _py_toBoolean, '_default': False})
boolean.construct = lambda v=None: construct(boolean, v)
boolean.__doc__ = """
    type of boolean value
    The following values are considered false:

    1. nullity value as explained above, see also `nullity`
    2. zero of any numeric type, for example, 0, 0.0
    3. length() return zero 
    
    reference: <https://docs.python.org/2/library/stdtypes.html#truth-value-testing>
    
    >>> false_values = [None, none, false, 0, 0.0, '', [], {}]
    >>> tuple(map(boolean, false_values))
    (False, False, False, False, False, False, False, False)
    
    >>> true_values = [true, -1, 1, 1.0, 'a', [0]]
    >>> tuple(map(boolean, true_values))
    (True, True, True, True, True, True)

"""


_py_id = id
@_.mixinTo([_, 'Object'])
def same(obj1, obj2):
    """
    return true if two objects are same object
    
    >>> v = [1,2,3]
    >>> w = v
    >>> a = [1,2,3]
    >>> same(v, v), same(w, v), same(a, v)
    (True, True, False)
    """
    
    return _py_id(obj1) == _py_id(obj2)
    
@_.mixinTo([_, 'Object'])
def clone(v):
    """
    make a shallow copy of object, return the new object
    
    >>> v = [1,2,3]
    >>> w = clone(v)
    >>> same(w, v)
    False
    """
    import copy
    return copy.copy(v)

@_.mixinTo([_, 'Type'])
def cast(type, v):
    """
    transform object type to another `type`
    
    >>> cast(int, "1"), cast(int, "-1")
    (1, -1)
    >>> cast(string, 1), cast(string, True), cast(string, None), cast(string, none)
    ('1', 'true', 'nil', '')
    
    when cast to same type, same object must returned.
    >>> v, w, x, y = 1, 'a', True, none
    >>> same(cast(int, v), v), same(cast(string, w), w), same(cast(boolean, x), x), same(cast(none, y), y)
    (True, True, True, True)
    
    
    
    """
    if same(type, none):
        return none
    if hasattr(type, '_realType'):
        return type(v)
    else:
        # TODO:
        pass

@_.mixinTo([_, 'Object'])
def castTo(v, type):
    """
    `castTo(v, type)` is same as `cast(type, v)`
    """
    return cast(type, v)
        
@_.mixinTo([_, 'Type'], [True, ("type", "a...")])
def is_(type, v):
    """
    return true if type of object is `type`
    >>> is_(none, none), is_(int, 1), is_(string, 'a'), is_(boolean, True)
    (True, True, True, True)
    """
    if same(type, none):
        return same(v, none)
    if same(v, none):
        return same(type, none)
    elif hasattr(type, '_realType'):
        return isinstance(v, type._realType)
    else:
        return isinstance(v, type)

@_.mixinTo([_, 'Object'])
def isType(v, type):
    """
    `isType``(v, type)` is same as `is_``(type, v)`
    """
    return is_(type, v)
    
    
    
def isSubclass(super, sub):
    return issubclass(super, sub)

def isSuperclass(sub, super):
    return isSubclass(super, sub)
    
_proxymap = dict( (t._realType, t) for t in [int, float, string, boolean] )

def typeOf(v):
    """
    return type of object
    
    >>> same(none, typeOf(none)), same(int, typeOf(1)), same(string, typeOf('a')), same(boolean, typeOf(True))
    (True, True, True, True)
    """
    if same(v, none):
        return none
    t = _py_typeOf(v)
    return _proxymap.get(t, t)
    

    