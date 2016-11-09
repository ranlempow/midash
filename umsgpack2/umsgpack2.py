# u-msgpack-python v2.3.0 - v at sergeev.io
# https://github.com/vsergeev/u-msgpack-python
#
# u-msgpack-python is a lightweight MessagePack serializer and deserializer
# module, compatible with both Python 2 and 3, as well CPython and PyPy
# implementations of Python. u-msgpack-python is fully compliant with the
# latest MessagePack specification.com/msgpack/msgpack/blob/master/spec.md). In
# particular, it supports the new binary, UTF-8 string, and application ext
# types.
#
# MIT License
#
# Copyright (c) 2013-2016 vsergeev / Ivan (Vanya) A. Sergeev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
"""
u-msgpack-python v2.3.0 - v at sergeev.io
https://github.com/vsergeev/u-msgpack-python

u-msgpack-python is a lightweight MessagePack serializer and deserializer
module, compatible with both Python 2 and 3, as well CPython and PyPy
implementations of Python. u-msgpack-python is fully compliant with the
latest MessagePack specification.com/msgpack/msgpack/blob/master/spec.md). In
particular, it supports the new binary, UTF-8 string, and application ext
types.

License: MIT
"""

__version__ = "3.0.0"
"Module version string"

version = (3,0,0)
"Module version tuple"

import struct
import collections
import sys
import io

################################################################################
### Ext Class
################################################################################

# Extension type for application-defined types and data
class Ext:
    """
    The Ext class facilitates creating a serializable extension object to store
    an application-defined type and data byte array.
    """

    def __init__(self, type, data):
        """
        Construct a new Ext object.

        Args:
            type: application-defined type integer from 0 to 127
            data: application-defined data byte array

        Raises:
            TypeError:
                Specified ext type is outside of 0 to 127 range.

        Example:
        >>> foo = umsgpack.Ext(0x05, b"\x01\x02\x03")
        >>> umsgpack.packb({u"special stuff": foo, u"awesome": True})
        '\x82\xa7awesome\xc3\xadspecial stuff\xc7\x03\x05\x01\x02\x03'
        >>> bar = umsgpack.unpackb(_)
        >>> print(bar["special stuff"])
        Ext Object (Type: 0x05, Data: 01 02 03)
        >>>
        """
        # Application ext type should be 0 <= type <= 127
        if not isinstance(type, int) or not (type >= 0 and type <= 127):
            raise TypeError("ext type out of range")
        # Check data is type bytes
        elif sys.version_info[0] == 3 and not isinstance(data, bytes):
            raise TypeError("ext data is not type \'bytes\'")
        elif sys.version_info[0] == 2 and not isinstance(data, str):
            raise TypeError("ext data is not type \'str\'")
        self.type = type
        self.data = data

    def __eq__(self, other):
        """
        Compare this Ext object with another for equality.
        """
        return (isinstance(other, self.__class__) and
                self.type == other.type and
                self.data == other.data)

    def __ne__(self, other):
        """
        Compare this Ext object with another for inequality.
        """
        return not self.__eq__(other)

    def __str__(self):
        """
        String representation of this Ext object.
        """
        s = "Ext Object (Type: 0x%02x, Data: " % self.type
        s += " ".join(["0x%02x" % ord(self.data[i:i+1]) for i in xrange(min(len(self.data), 8))])
        if len(self.data) > 8:
            s += " ..."
        s += ")"
        return s

class InvalidString(bytes):
    """Subclass of bytes to hold invalid UTF-8 strings."""
    pass

################################################################################
### Exceptions
################################################################################

# Base Exception classes
class PackException(Exception):
    "Base class for exceptions encountered during packing."
    pass
class UnpackException(Exception):
    "Base class for exceptions encountered during unpacking."
    pass

# Packing error
class UnsupportedTypeException(PackException):
    "Object type not supported for packing."
    pass

# Unpacking error
class InsufficientDataException(UnpackException):
    "Insufficient data to unpack the serialized object."
    pass
class InvalidStringException(UnpackException):
    "Invalid UTF-8 string encountered during unpacking."
    pass
class ReservedCodeException(UnpackException):
    "Reserved code encountered during unpacking."
    pass
class UnhashableKeyException(UnpackException):
    """
    Unhashable key encountered during map unpacking.
    The serialized map cannot be deserialized into a Python dictionary.
    """
    pass
class DuplicateKeyException(UnpackException):
    "Duplicate key encountered during map unpacking."
    pass

# Backwards compatibility
KeyNotPrimitiveException = UnhashableKeyException
KeyDuplicateException = DuplicateKeyException

################################################################################
### Exported Functions and Globals
################################################################################

# Exported functions and variables, set up in __init()
pack = None
packb = None
unpack = None
unpackb = None
dump = None
dumps = None
load = None
loads = None

compatibility = False
"""
Compatibility mode boolean.

When compatibility mode is enabled, u-msgpack-python will serialize both
unicode strings and bytes into the old "raw" msgpack type, and deserialize the
"raw" msgpack type into bytes. This provides backwards compatibility with the
old MessagePack specification.

Example:
>>> umsgpack.compatibility = True
>>>
>>> umsgpack.packb([u"some string", b"some bytes"])
b'\x92\xabsome string\xaasome bytes'
>>> umsgpack.unpackb(_)
[b'some string', b'some bytes']
>>>
"""


################################################################################
### Packing
################################################################################

# You may notice _pack_uint8(obj) instead of the simpler chr(obj) in the
# code below. This is to allow for seamless Python 2 and 3 compatibility, as
# chr(obj) has a str return type instead of bytes in Python 3, and
# struct.pack(...) has the right return type in both versions.


_pack_int8   = struct.Struct("b").pack
_pack_int16  = struct.Struct(">h").pack
_pack_int32  = struct.Struct(">i").pack
_pack_int64  = struct.Struct(">q").pack
_pack_uint8  = struct.Struct("B").pack
_pack_uint16 = struct.Struct(">H").pack
_pack_uint32 = struct.Struct(">I").pack
_pack_uint64 = struct.Struct(">Q").pack
_pack_float32 = struct.Struct(">f").pack
_pack_float64 = struct.Struct(">d").pack

def _make_packfuncs(
        len=len,
        _pack_int8=_pack_int8, _pack_int16=_pack_int16, _pack_int32=_pack_int32, _pack_int64=_pack_int64,
        _pack_uint8=_pack_uint8, _pack_uint16=_pack_uint16, _pack_uint32=_pack_uint32, _pack_uint64=_pack_uint64,
        _pack_float32=_pack_float32, _pack_float64=_pack_float64
    ):
    
    def _pack_integer(obj, fwrite, options):
        if obj < 0:
            if obj >= -32:
                fwrite(_pack_int8(obj))
            elif obj >= -2**(8-1):
                fwrite(b"\xd0" + _pack_int8(obj))
            elif obj >= -2**(16-1):
                fwrite(b"\xd1" + _pack_int16(obj))
            elif obj >= -2**(32-1):
                fwrite(b"\xd2" + _pack_int32(obj))
            elif obj >= -2**(64-1):
                fwrite(b"\xd3" + _pack_int64(obj))
            else:
                raise UnsupportedTypeException("huge signed int")
        else:
            if obj <= 127:
                fwrite(_pack_uint8(obj))
            elif obj <= 2**8-1:
                fwrite(b"\xcc" + _pack_uint8(obj))
            elif obj <= 2**16-1:
                fwrite(b"\xcd" + _pack_uint16(obj))
            elif obj <= 2**32-1:
                fwrite(b"\xce" + _pack_uint32(obj))
            elif obj <= 2**64-1:
                fwrite(b"\xcf" + _pack_uint64(obj))
            else:
                raise UnsupportedTypeException("huge unsigned int")

    def _pack_nil(obj, fwrite, options):
        fwrite(b"\xc0")

    def _pack_boolean(obj, fwrite, options):
        fwrite(b"\xc3" if obj else b"\xc2")

    if _float_size == 64:
        def _pack_float(obj, fwrite, options):
            fwrite(b"\xcb" + _pack_float64(obj))
    else:
        def _pack_float(obj, fwrite, options):
            fwrite(b"\xca" + _pack_float32(obj))
    
    def _pack_string(obj, fwrite, options):
        obj = obj.encode('utf-8')
        ln = len(obj)
        if ln <= 31:
            fwrite(_pack_uint8(0xa0 | ln) + obj)
        elif ln <= 2**8-1:
            fwrite(b"\xd9" + _pack_uint8(ln) + obj)
        elif ln <= 2**16-1:
            fwrite(b"\xda" + _pack_uint16(ln) + obj)
        elif ln <= 2**32-1:
            fwrite(b"\xdb" + _pack_uint32(ln) + obj)
        else:
            raise UnsupportedTypeException("huge string")

    def _pack_binary(obj, fwrite, options):
        ln = len(obj)
        if ln <= 2**8-1:
            fwrite(b"\xc4" + _pack_uint8(ln) + obj)
        elif ln <= 2**16-1:
            fwrite(b"\xc5" + _pack_uint16(ln) + obj)
        elif ln <= 2**32-1:
            fwrite(b"\xc6" + _pack_uint32(ln) + obj)
        else:
            raise UnsupportedTypeException("huge binary string")
            
    # TODO:
    def _pack_ext(obj, fwrite, options):
        if len(obj.data) == 1:
            fwrite(b"\xd4" + struct.pack("B", obj.type & 0xff) + obj.data)
        elif len(obj.data) == 2:
            fwrite(b"\xd5" + struct.pack("B", obj.type & 0xff) + obj.data)
        elif len(obj.data) == 4:
            fwrite(b"\xd6" + struct.pack("B", obj.type & 0xff) + obj.data)
        elif len(obj.data) == 8:
            fwrite(b"\xd7" + struct.pack("B", obj.type & 0xff) + obj.data)
        elif len(obj.data) == 16:
            fwrite(b"\xd8" + struct.pack("B", obj.type & 0xff) + obj.data)
        elif len(obj.data) <= 2**8-1:
            fwrite(b"\xc7" + struct.pack("BB", len(obj.data), obj.type & 0xff) + obj.data)
        elif len(obj.data) <= 2**16-1:
            fwrite(b"\xc8" + struct.pack(">HB", len(obj.data), obj.type & 0xff) + obj.data)
        elif len(obj.data) <= 2**32-1:
            fwrite(b"\xc9" + struct.pack(">IB", len(obj.data), obj.type & 0xff) + obj.data)
        else:
            raise UnsupportedTypeException("huge ext data")

    def _pack_array(obj, fwrite, options):
        ln = len(obj)
        if ln <= 15:
            fwrite(_pack_uint8(0x90 | ln))
        elif ln <= 2**16-1:
            fwrite(b"\xdc" + _pack_uint16(ln))
        elif ln <= 2**32-1:
            fwrite(b"\xdd" + _pack_uint32(ln))
        else:
            raise UnsupportedTypeException("huge array")

        for e in obj:
            #pack(e, fwrite, options)
            _pack_dispatch_table[e.__class__](e, fwrite, options)
            
    def _pack_map(obj, fwrite, options):
        ln = len(obj)
        if ln <= 15:
            fwrite(_pack_uint8(0x80 | ln))
        elif ln <= 2**16-1:
            fwrite(b"\xde" + _pack_uint16(ln))
        elif ln <= 2**32-1:
            fwrite(b"\xdf" + _pack_uint32(ln))
        else:
            raise UnsupportedTypeException("huge array")

        for k,v in obj.items():
            #pack(k, fwrite, options)
            #pack(v, fwrite, options)
            _pack_dispatch_table[k.__class__](k, fwrite, options)
            _pack_dispatch_table[v.__class__](v, fwrite, options)
            
    if sys.version_info[0] == 3:
        _pack_dispatch_table = {
            None.__class__: _pack_nil,
            bool: _pack_boolean,
            int: _pack_integer,
            float: _pack_float,
            str: _pack_string,
            bytes: _pack_binary,
            list: _pack_array,
            tuple: _pack_array,
            dict: _pack_map,
            collections.OrderedDict: _pack_map,
            Ext: _pack_ext,
        }
    else:
        _pack_dispatch_table = {
            None.__class__: _pack_nil,
            bool: _pack_boolean,
            int: _pack_integer,
            long: _pack_integer,
            float: _pack_float,
            unicode: _pack_string,
            str: _pack_binary,
            list: _pack_array,
            tuple: _pack_array,
            dict: _pack_map,
            collections.OrderedDict: _pack_map,
            Ext: _pack_ext,
        }
    
    def _pack_unknow(obj, fwrite, option):
        raise UnsupportedTypeException("unsupported type: %s" % str(type(obj)))
    
    def _pack3(obj, fp, options={}):
        return _pack_dispatch_table.get(obj.__class__, _pack_unknow)(obj, fp.write, options)
        
    _pack2 = _pack3
    
    def _packb2(obj, options={}):
        fp = io.BytesIO()
        _pack2(obj, fp, options)
        return fp.getvalue()

    def _packb3(obj, options={}):
        fp = io.BytesIO()
        _pack3(obj, fp, options)
        return fp.getvalue()
    return _pack2, _packb2, _pack3, _packb3
    
    


    
    
    
    
    
    

################################################################################
### Unpacking
################################################################################

_unpack_int8   = struct.Struct("b").unpack
_unpack_int16  = struct.Struct(">h").unpack
_unpack_int32  = struct.Struct(">i").unpack
_unpack_int64  = struct.Struct(">q").unpack
_unpack_uint8  = struct.Struct("B").unpack
_unpack_uint16 = struct.Struct(">H").unpack
_unpack_uint32 = struct.Struct(">I").unpack
_unpack_uint64 = struct.Struct(">Q").unpack
_unpack_float32 = struct.Struct(">f").unpack
_unpack_float64 = struct.Struct(">d").unpack

def _make_unpackfuncs(
        len=len, ord=ord, xrange=range, decode=bytes.decode,
        _unpack_int8=_unpack_int8, _unpack_int16=_unpack_int16, _unpack_int32=_unpack_int32, _unpack_int64=_unpack_int64,
        _unpack_uint8=_unpack_uint8, _unpack_uint16=_unpack_uint16, _unpack_uint32=_unpack_uint32, _unpack_uint64=_unpack_uint64,
        _unpack_float32=_unpack_float32, _unpack_float64=_unpack_float64
    ):

    def _unpack_reserved(code, fread, options):
        if code == b'\xc1':
            raise ReservedCodeException("encountered reserved code: 0x%02x" % ord(code))
        raise Exception("logic error, not reserved code: 0x%02x" % ord(code))

    
    def _unpack_ext(code, fread, options):
        if code == b'\xd4':
            length = 1
        elif code == b'\xd5':
            length = 2
        elif code == b'\xd6':
            length = 4
        elif code == b'\xd7':
            length = 8
        elif code == b'\xd8':
            length = 16
        elif code == b'\xc7':
            length = _unpack_uint8(fread(1))[0]
        elif code == b'\xc8':
            length = _unpack_uint16(fread(2))[0]
        elif code == b'\xc9':
            length = _unpack_uint32(fread(4))[0]
        else:
            raise Exception("logic error, not ext: 0x%02x" % ord(code))
        
        ext = Ext(ord(fread(1)), fread(length))

        # Unpack with ext handler, if we have one
        ext_handlers = options.get("ext_handlers")
        if ext_handlers and ext.type in ext_handlers:
            ext = ext_handlers[ext.type](ext)

        return ext

    def _unpack_array(code, fread, options):
        if (ord(code) & 0xf0) == 0x90:
            length = (ord(code) & ~0xf0)
        elif code == b'\xdc':
            length = _unpack_uint16(fread(2))[0]
        elif code == b'\xdd':
            length = _unpack_uint32(fread(4))[0]
        else:
            raise Exception("logic error, not array: 0x%02x" % ord(code))
            
        def _unpack_item():
            code = fread(1)
            return _unpack_dispatch_table[code](code, fread, options)
        return [ _unpack_item() for i in xrange(length) ]

        
    def _deep_list_to_tuple(obj):
        if isinstance(obj, list):
            return tuple([_deep_list_to_tuple(e) for e in obj])
        return obj

        
    def _unpack_map(code, fread, options):
        if (ord(code) & 0xf0) == 0x80:
            length = (ord(code) & ~0xf0)
        elif code == b'\xde':
            length = _unpack_uint16(fread(2))[0]
        elif code == b'\xdf':
            length = _unpack_uint32(fread(4))[0]
        else:
            raise Exception("logic error, not map: 0x%02x" % ord(code))
        
        d = {} if not options.get('use_ordered_dict') else collections.OrderedDict()
        for _ in xrange(length):
            # Unpack key
            code = fread(1)
            k = _unpack_dispatch_table[code](code, fread, options)
            
            if k.__class__ == list:
                # Attempt to convert list into a hashable tuple
                k = _deep_list_to_tuple(k)
            
            # Unpack value
            code = fread(1)
            v = _unpack_dispatch_table[code](code, fread, options)

            try:
                d[k] = v
            except TypeError:
                raise UnhashableKeyException("encountered unhashable key: %s" % str(k))
        return d

    def _unpack(fp, options):
        try:
            code = fp.read(1)
            return _unpack_dispatch_table[code](code, fp.read, options)
        except struct.error:
            raise InsufficientDataException()
        except UnicodeDecodeError:
            # if options.get("allow_invalid_utf8"):
                # return InvalidString(data)
            raise InvalidStringException("unpacked string is invalid utf-8")
            
            
    ########################################

    def _unpack2(fp, **options):
        """
        Deserialize MessagePack bytes into a Python object.

        Args:
            fp: a .read()-supporting file-like object

        Kwargs:
            ext_handlers (dict): dictionary of Ext handlers, mapping integer Ext
                                 type to a callable that unpacks an instance of
                                 Ext into an object
            use_ordered_dict (bool): unpack maps into OrderedDict, instead of
                                     unordered dict (default False)
            allow_invalid_utf8 (bool): unpack invalid strings into instances of
                                       InvalidString, for access to the bytes
                                       (default False)

        Returns:
            A Python object.

        Raises:
            InsufficientDataException(UnpackException):
                Insufficient data to unpack the serialized object.
            InvalidStringException(UnpackException):
                Invalid UTF-8 string encountered during unpacking.
            ReservedCodeException(UnpackException):
                Reserved code encountered during unpacking.
            UnhashableKeyException(UnpackException):
                Unhashable key encountered during map unpacking.
                The serialized map cannot be deserialized into a Python dictionary.
            DuplicateKeyException(UnpackException):
                Duplicate key encountered during map unpacking.

        Example:
        >>> f = open('test.bin', 'rb')
        >>> umsgpack.unpackb(f)
        {u'compact': True, u'schema': 0}
        >>>
        """
        return _unpack(fp, options)

    def _unpack3(fp, **options):
        return _unpack(fp, options)

    # For Python 2, expects a str object
    def _unpackb2(s, **options):
        if not isinstance(s, (str, bytearray)):
            raise TypeError("packed data must be type 'str' or 'bytearray'")
        return _unpack(io.BytesIO(s), options)

    # For Python 3, expects a bytes object
    def _unpackb3(s, **options):
        if not isinstance(s, (bytes, bytearray)):
            raise TypeError("packed data must be type 'bytes' or 'bytearray'")
        return _unpack(io.BytesIO(s), options)

    # Build a dispatch table for fast lookup of unpacking function

    _unpack_dispatch_table = {}
    def _unpack_insufficient(code, fread, options):
        raise InsufficientDataException()
    _unpack_dispatch_table[b''] = _unpack_insufficient
    
    # Fix uint
    for n in range(0, 0x7f+1):
        code = struct.pack("B", n)
        _unpack_dispatch_table[code] = (lambda n: lambda _1, _2, _3: n)(_unpack_uint8(code)[0])
    # Fix map
    for code in range(0x80, 0x8f+1):
        _unpack_dispatch_table[struct.pack("B", code)] = _unpack_map
    # Fix array
    for code in range(0x90, 0x9f+1):
        _unpack_dispatch_table[struct.pack("B", code)] = _unpack_array
        
    # Fix str
    for n in range(0xa0, 0xbf+1):
        _unpack_dispatch_table[struct.pack("B", n)] = (lambda n: lambda _1, fread, _3: decode(fread(n), 'utf-8'))(n - 0xa0)
        
    # Nil
    _unpack_dispatch_table[b'\xc0'] = lambda _1, _2, _3: None
    # Reserved
    _unpack_dispatch_table[b'\xc1'] = _unpack_reserved
    # Boolean
    _unpack_dispatch_table[b'\xc2'] = lambda _1, _2, _3: False
    _unpack_dispatch_table[b'\xc3'] = lambda _1, _2, _3: True
    # Bin
    _unpack_dispatch_table[b'\xc4'] = lambda code, fread, _3: fread(_unpack_uint8(fread(1))[0])
    _unpack_dispatch_table[b'\xc5'] = lambda code, fread, _3: fread(_unpack_uint16(fread(2))[0])
    _unpack_dispatch_table[b'\xc6'] = lambda code, fread, _3: fread(_unpack_uint32(fread(4))[0])
    
    # Ext
    for code in range(0xc7, 0xc9+1):
        _unpack_dispatch_table[struct.pack("B", code)] = _unpack_ext
    # Float
    _unpack_dispatch_table[b'\xca'] = lambda _1, fread, _3: _unpack_float32(fread(4))[0]
    _unpack_dispatch_table[b'\xcb'] = lambda _1, fread, _3: _unpack_float64(fread(8))[0]
    
    # Uint
    _unpack_dispatch_table[b'\xcc'] = lambda _1, fread, _3: _unpack_uint8(fread(1))[0]
    _unpack_dispatch_table[b'\xcd'] = lambda _1, fread, _3: _unpack_uint16(fread(2))[0]
    _unpack_dispatch_table[b'\xce'] = lambda _1, fread, _3: _unpack_uint32(fread(4))[0]
    _unpack_dispatch_table[b'\xcf'] = lambda _1, fread, _3: _unpack_uint64(fread(8))[0]
    # Int
    _unpack_dispatch_table[b'\xd0'] = lambda _1, fread, _3: _unpack_int8(fread(1))[0]
    _unpack_dispatch_table[b'\xd1'] = lambda _1, fread, _3: _unpack_int16(fread(2))[0]
    _unpack_dispatch_table[b'\xd2'] = lambda _1, fread, _3: _unpack_int32(fread(4))[0]
    _unpack_dispatch_table[b'\xd3'] = lambda _1, fread, _3: _unpack_int64(fread(8))[0]
        
    # Fixext
    for code in range(0xd4, 0xd8+1):
        _unpack_dispatch_table[struct.pack("B", code)] = _unpack_ext
    # String
    _unpack_dispatch_table[b'\xd9'] = lambda _1, fread, _3: decode(fread(_unpack_uint8(fread(1))[0]), 'utf-8')
    _unpack_dispatch_table[b'\xda'] = lambda _1, fread, _3: decode(fread(_unpack_uint16(fread(2))[0]), 'utf-8')
    _unpack_dispatch_table[b'\xdb'] = lambda _1, fread, _3: decode(fread(_unpack_uint32(fread(4))[0]), 'utf-8')
    # Array
    _unpack_dispatch_table[b'\xdc'] = _unpack_array
    _unpack_dispatch_table[b'\xdd'] = _unpack_array
    # Map
    _unpack_dispatch_table[b'\xde'] = _unpack_map
    _unpack_dispatch_table[b'\xdf'] = _unpack_map
    # Negative fixint
    for n in range(0xe0, 0xff+1):
        code = struct.pack("B", n)
        _unpack_dispatch_table[code] = (lambda n: lambda _1, _2, _3: n)(_unpack_int8(code)[0])
        
    return _unpack2, _unpackb2, _unpack3, _unpackb3


################################################################################
### Module Initialization
################################################################################

def __init():
    global pack
    global packb
    global unpack
    global unpackb
    global dump
    global dumps
    global load
    global loads
    global compatibility
    global _float_size
    # global _unpack_dispatch_table
    # global xrange

    # Compatibility mode for handling strings/bytes with the old specification
    compatibility = False

    # Auto-detect system float precision
    if sys.float_info.mant_dig == 53:
        _float_size = 64
    else:
        _float_size = 32

    _pack2, _packb2, _pack3, _packb3 = _make_packfuncs()
    _unpack2, _unpackb2, _unpack3, _unpackb3 = _make_unpackfuncs()
    
    # Map packb and unpackb to the appropriate version
    if sys.version_info[0] == 3:
        pack = _pack3
        packb = _packb3
        dump = _pack3
        dumps = _packb3
        unpack = _unpack3
        unpackb = _unpackb3
        load = _unpack3
        loads = _unpackb3
        xrange = range
    else:
        pack = _pack2
        packb = _packb2
        dump = _pack2
        dumps = _packb2
        unpack = _unpack2
        unpackb = _unpackb2
        load = _unpack2
        loads = _unpackb2

    

__init()
