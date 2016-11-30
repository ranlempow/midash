Modules
-------
| Module | Description |
|--------|-------------|
| [lang](#module-lang) | --- |
| [math](#module-math) | --- |

Module *lang*
===========
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

Contents
--------
| Signature | Description |
|-----------|-------------|
| [__`_.cast(`__*`type, v`*__`)`__](#cast) |     transform object type to another `type` |
| [__`_.castTo(`__*`v, type`*__`)`__](#castto) |     `castTo(v, type)` is same as `cast(type, v)` |
| [__`_.clone(`__*`v`*__`)`__](#clone) |     make a shallow copy of object, return the ...  |
| [__`_.construct(`__*`type, [value]`*__`)`__](#construct) |     create new object of `type`, if `value` i ...  |
| [__`_.isSubclass(`__*`super, sub`*__`)`__](#issubclass) |  |
| [__`_.isSuperclass(`__*`sub, super`*__`)`__](#issuperclass) |  |
| [__`_.isType(`__*`v, type`*__`)`__](#istype) |     `isType``(v, type)` is same as `is_``(typ ...  |
| [__`_.is_(`__*`type, v`*__`)`__](#is_) |     return true if type of object is `type` |
| [__`_.nullity(`__*`value`*__`)`__](#nullity) |     null is a value of undefined variable or  ...  |
| [__`_.same(`__*`obj1, obj2`*__`)`__](#same) |     return true if two objects are same object |
| [__`_.typeOf(`__*`v`*__`)`__](#typeof) |     return type of object |
| [__`_.false `__*` `*__` `__](#false) | bool(x) -> bool |
| [__`_.true `__*` `*__` `__](#true) | bool(x) -> bool |
| [__`_.boolean(`__*` `*__`)`__](#boolean) |     type of boolean value |
| [__`_.float(`__*` `*__`)`__](#float) |     type of float-point number |
| [__`_.int(`__*` `*__`)`__](#int) |     type of integer number |
| [__`_.none(`__*` `*__`)`__](#none) |     type of nullity value |
| [__`_.string(`__*` `*__`)`__](#string) |     type of string |

Defines
-------
### cast
- __`_.cast(`__*`type, v`*__`)`__
- __`Type.cast(`__*`v`*__`)`__

transform object type to another `type`

    >>> cast(int, "1"), cast(int, "-1")
    (1, -1)
    >>> cast(string, 1), cast(string, True), cast(string, None), cast(string, none)
    ('1', 'true', 'nil', '')

when cast to same type, same object must returned.

    >>> v, w, x, y = 1, 'a', True, none
    >>> same(cast(int, v), v), same(cast(string, w), w), same(cast(boolean, x), x), same(cast(none, y), y)
    (True, True, True, True)
- - - - - - - - - - - -

### castTo
- __`_.castTo(`__*`v, type`*__`)`__
- __`Object.castTo(`__*`type`*__`)`__

`castTo(v, type)` is same as `cast(type, v)`
- - - - - - - - - - - -

### clone
- __`_.clone(`__*`v`*__`)`__
- __`Object.clone(`__*` `*__`)`__

make a shallow copy of object, return the new object

    >>> v = [1,2,3]
    >>> w = clone(v)
    >>> same(w, v)
    False
- - - - - - - - - - - -

### construct
- __`_.construct(`__*`type, [value]`*__`)`__
- __`Type.construct(`__*`[value]`*__`)`__

create new object of `type`, if `value` is not given, empty value of that type is returned.

    >>> int(), float(), string(), boolean(), none()
    (0, 0.0, '', False, <class none>)
    >>> int.construct(12)
    12

special construct

    >>> float('inf'), -float('inf'), float('nan')
    (inf, -inf, nan)
- - - - - - - - - - - -

### isSubclass
- __`_.isSubclass(`__*`super, sub`*__`)`__

- - - - - - - - - - - -

### isSuperclass
- __`_.isSuperclass(`__*`sub, super`*__`)`__

- - - - - - - - - - - -

### isType
- __`_.isType(`__*`v, type`*__`)`__
- __`Object.isType(`__*`type`*__`)`__

[`isType`](#istype)`(v, type)` is same as [`is_`](#is_)`(type, v)`
- - - - - - - - - - - -

### is_
- __`_.is_(`__*`type, v`*__`)`__
- __`_.is_(`__*`type, a...`*__`)`__
- __`Type.is_(`__*`v`*__`)`__
- __`Type.is_(`__*`a...`*__`)`__

return true if type of object is `type`

    >>> is_(none, none), is_(int, 1), is_(string, 'a'), is_(boolean, True)
    (True, True, True, True)
- - - - - - - - - - - -

### nullity
- __`_.nullity(`__*`value`*__`)`__

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
- - - - - - - - - - - -

### same
- __`_.same(`__*`obj1, obj2`*__`)`__
- __`Object.same(`__*`obj2`*__`)`__

return true if two objects are same object

    >>> v = [1,2,3]
    >>> w = v
    >>> a = [1,2,3]
    >>> same(v, v), same(w, v), same(a, v)
    (True, True, False)
- - - - - - - - - - - -

### typeOf
- __`_.typeOf(`__*`v`*__`)`__

return type of object

    >>> same(none, typeOf(none)), same(int, typeOf(1)), same(string, typeOf('a')), same(boolean, typeOf(True))
    (True, True, True, True)
- - - - - - - - - - - -

### false
- __`_.false `__*` `*__` `__

false symbol 
- - - - - - - - - - - -

### true
- __`_.true `__*` `*__` `__

truth symbol 
- - - - - - - - - - - -

### boolean
- __`_.boolean(`__*` `*__`)`__

type of boolean value
The following values are considered false:

1. nullity value as explained above, see also [`nullity`](#nullity)
2. zero of any numeric type, for example, 0, 0.0
3. length() return zero 

reference: <https://docs.python.org/2/library/stdtypes.html#truth-value-testing>

    >>> false_values = [None, none, false, 0, 0.0, '', [], {}]
    >>> tuple(map(boolean, false_values))
    (False, False, False, False, False, False, False, False)

    >>> true_values = [true, -1, 1, 1.0, 'a', [0]]
    >>> tuple(map(boolean, true_values))
    (True, True, True, True, True, True)
- - - - - - - - - - - -

### float
- __`_.float(`__*` `*__`)`__

type of float-point number
- - - - - - - - - - - -

### int
- __`_.int(`__*` `*__`)`__

type of integer number
- - - - - - - - - - - -

### none
- __`_.none(`__*` `*__`)`__

type of nullity value

functions should not return none, this value is not default value of returning
- - - - - - - - - - - -

### string
- __`_.string(`__*` `*__`)`__

type of string
- - - - - - - - - - - -

Module *math*
===========

Contents
--------
| Signature | Description |
|-----------|-------------|
| [__`_.abs(`__*`...`*__`)`__](#abs) | abs(number) -> number |
| [__`_.acos(`__*`...`*__`)`__](#acos) | acos(x) |
| [__`_.asin(`__*`...`*__`)`__](#asin) | asin(x) |
| [__`_.atan(`__*`...`*__`)`__](#atan) | atan(x) |
| [__`_.atan2(`__*`...`*__`)`__](#atan2) | atan2(y, x) |
| [__`_.ceil(`__*`...`*__`)`__](#ceil) | ceil(x) |
| [__`_.cos(`__*`...`*__`)`__](#cos) | cos(x) |
| [__`_.divmod(`__*`...`*__`)`__](#divmod) | divmod(x, y) -> (div, mod) |
| [__`_.exp(`__*`...`*__`)`__](#exp) | exp(x) |
| [__`_.floor(`__*`...`*__`)`__](#floor) | floor(x) |
| [__`_.log(`__*`...`*__`)`__](#log) | log(x[, base]) |
| [__`_.max(`__*`...`*__`)`__](#max) | max(iterable, *[, default=obj, key=func]) ->  ...  |
| [__`_.min(`__*`...`*__`)`__](#min) | min(iterable, *[, default=obj, key=func]) ->  ...  |
| [__`_.round(`__*`...`*__`)`__](#round) | round(number[, ndigits]) -> number |
| [__`_.sin(`__*`...`*__`)`__](#sin) | sin(x) |
| [__`_.sum(`__*`...`*__`)`__](#sum) | sum(iterable[, start]) -> value |
| [__`_.tan(`__*`...`*__`)`__](#tan) | tan(x) |

Defines
-------
### abs
- __`_.abs(`__*`...`*__`)`__

abs(number) -> number

Return the absolute value of the argument.
- - - - - - - - - - - -

### acos
- __`_.acos(`__*`...`*__`)`__

acos(x)

Return the arc cosine (measured in radians) of x.
- - - - - - - - - - - -

### asin
- __`_.asin(`__*`...`*__`)`__

asin(x)

Return the arc sine (measured in radians) of x.
- - - - - - - - - - - -

### atan
- __`_.atan(`__*`...`*__`)`__

atan(x)

Return the arc tangent (measured in radians) of x.
- - - - - - - - - - - -

### atan2
- __`_.atan2(`__*`...`*__`)`__

atan2(y, x)

Return the arc tangent (measured in radians) of y/x.
Unlike atan(y/x), the signs of both x and y are considered.
- - - - - - - - - - - -

### ceil
- __`_.ceil(`__*`...`*__`)`__

ceil(x)

Return the ceiling of x as an int.
This is the smallest integral value >= x.
- - - - - - - - - - - -

### cos
- __`_.cos(`__*`...`*__`)`__

cos(x)

Return the cosine of x (measured in radians).
- - - - - - - - - - - -

### divmod
- __`_.divmod(`__*`...`*__`)`__

divmod(x, y) -> (div, mod)

Return the tuple ((x-x%y)/y, x%y).  Invariant: div*y + mod == x.
- - - - - - - - - - - -

### exp
- __`_.exp(`__*`...`*__`)`__

exp(x)

Return e raised to the power of x.
- - - - - - - - - - - -

### floor
- __`_.floor(`__*`...`*__`)`__

floor(x)

Return the floor of x as an int.
This is the largest integral value <= x.
- - - - - - - - - - - -

### log
- __`_.log(`__*`...`*__`)`__

log(x[, base])

Return the logarithm of x to the given base.
If the base not specified, returns the natural logarithm (base e) of x.
- - - - - - - - - - - -

### max
- __`_.max(`__*`...`*__`)`__

max(iterable, *[, default=obj, key=func]) -> value
max(arg1, arg2, *args, *[, key=func]) -> value

With a single iterable argument, return its biggest item. The
default keyword-only argument specifies an object to return if
the provided iterable is empty.
With two or more arguments, return the largest argument.
- - - - - - - - - - - -

### min
- __`_.min(`__*`...`*__`)`__

min(iterable, *[, default=obj, key=func]) -> value
min(arg1, arg2, *args, *[, key=func]) -> value

With a single iterable argument, return its smallest item. The
default keyword-only argument specifies an object to return if
the provided iterable is empty.
With two or more arguments, return the smallest argument.
- - - - - - - - - - - -

### round
- __`_.round(`__*`...`*__`)`__

round(number[, ndigits]) -> number

Round a number to a given precision in decimal digits (default 0 digits).
This returns an int when called with one argument, otherwise the
same type as the number. ndigits may be negative.
- - - - - - - - - - - -

### sin
- __`_.sin(`__*`...`*__`)`__

sin(x)

Return the sine of x (measured in radians).
- - - - - - - - - - - -

### sum
- __`_.sum(`__*`...`*__`)`__

sum(iterable[, start]) -> value

Return the sum of an iterable of numbers (NOT strings) plus the value
of parameter 'start' (which defaults to 0).  When the iterable is
empty, return start.
- - - - - - - - - - - -

### tan
- __`_.tan(`__*`...`*__`)`__

tan(x)

Return the tangent of x (measured in radians).
- - - - - - - - - - - -
