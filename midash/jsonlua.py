#
# json.lua
#
# Copyright (c) 2015 rxi
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the MIT license. See LICENSE for details.
#

import re
import math

#######################################
# Encode
#######################################

# local encode

escape_char_map = {
    "\\" : "\\\\",
    "\"" : "\\\"",
    "\b" : "\\b",
    "\f" : "\\f",
    "\n" : "\\n",
    "\r" : "\\r",
    "\t" : "\\t",
}


escape_char_map_inv = { "\\/": "/" }
for k, v in escape_char_map.items():
    escape_char_map_inv[v] = k


def escape_char(c, stack=None):
    esc = escape_char_map.get(c, None)
    if esc is not None:
        return esc
    return escape_char_map.getdefault(c, "\\u%04x" % ord(c) )

    
def encode_list(val, fwrite, stack=None):
    stack = stack or {}
    if id(val) in stack:
        raise Exception("circular reference")
    stack[id(val)] = True
    
    more = False
    fwrite( "[" )
    for e in val:
        if more:
            fwrite( "," )
        else:
            more = True
            
        type_func_map[e.__class__](e, fwrite, stack)
        
    fwrite( "]" )
    del stack[id(val)]
    
def encode_dict(val, fwrite, stack=None):
    stack = stack or {}
    if id(val) in stack:
        raise Exception("circular reference")
    stack[id(val)] = True
    
    
    more = False
    fwrite( "{" )
    for k, v in val.items():
        if k.__class__ != str:
            raise Exception("invalid table: mixed or invalid key types")
        if more:
            fwrite( "," )
        else:
            more = True
        
        type_func_map[k.__class__](k, fwrite, stack)
        fwrite(":")
        type_func_map[v.__class__](v, fwrite, stack)
        
    fwrite( "}" )
    del stack[id(val)]

def encode_string(val, fwrite, stack=None, len=len):
    if len(val) < 64:
        fwrite( '"' + val + '"' )
        return
    fwrite( '"' )
    fwrite( val )
    fwrite( '"' )
    # return '"' .. val:gsub('[%z\1-\31\\"]', escape_char) .. '"'

def encode_number(val, fwrite, stack=None, str=str):
    # Check for NaN, -inf and inf
    # if val ~= val or val <= -math.huge or val >= math.huge:
        # raise Exception("unexpected number value '" + str(val) + "'")
    fwrite( str(val) )
    # return string.format("%.14g", val)
    
type_func_map = {
    None.__class__: lambda val, fwrite, _3=None: fwrite("null"),
    bool:           lambda val, fwrite, _3=None: fwrite("true") if val else fwrite("false"),
    str:            encode_string,
    int:            encode_number,
    float:          encode_number,
    list:           encode_list,
    tuple:          encode_list,
    dict:           encode_dict,
}
    
def _encode(val, fwrite, stack=None):
    type_func_map[val.__class__](val, fwrite, stack)

def encode(val):
    import io
    fp = io.StringIO()
    _encode(val, fp.write)
    return fp.getvalue()
    
dumps = encode

# print(encode({'a':[1,{}]}))



#######################################
# Decode
#######################################


def make_parse_functions(
        array_creator=None,
        object_creator=None,
        fint_not_space_chars = re.compile(r'[ \t\r\n]*').search,
        find_delim_chars     = re.compile(r'[^ \t\r\n\]\}\,]*').search,
        literal_table        = { "true": True, "false": False, "null": None},
        float=float, int=int, str=str
    ):

    # space_chars   = set([" ", "\t", "\r", "\n"])
    # delim_chars   = set([" ", "\t", "\r", "\n", "]", "}", ","])
    escape_chars  = set(["\\", "/", '"', "b", "f", "n", "r", "t", "u"])
    # literals      = set(["true", "false", "null"])

    '''
    def next_char(string, idx, set, negate=False):
        for i in range(idx, len(string)):
            if (string[i] in set) != negate:
                return i
        return len(string) +1
    '''
    
    def decode_error(str, idx, msg):
        line_count = 1
        col_count = 1
        for i in range(0, idx):
            col_count += 1
            if str[i] == "\n":
                line_count += 1
                col_count = 1
        raise Exception("%s at line %d col %d" % (msg, line_count, col_count))


    def codepoint_to_utf8(n, f=math.floor):
        if n <= 0x7f:
            return chr(n)
        elif n <= 0x7ff:
            return chr(f(n / 64) + 192) + chr(n % 64 + 128)
        elif n <= 0xffff:
            return chr(f(n / 4096) + 224) + chr(f(n % 4096 / 64) + 128) +  chr(n % 64 + 128)
        elif n <= 0x10ffff:
            return chr(f(n / 262144) + 240) + chr(f(n % 262144 / 4096) + 128) + chr(f(n % 4096 / 64) + 128) + chr(n % 64 + 128)
        raise Exception("invalid unicode codepoint '%x'" % n)
        
    '''
    local function codepoint_to_utf8(n)
      # http://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=iws-appendixa
      local f = math.floor
      if n <= 0x7f then
        return string.char(n)
      elseif n <= 0x7ff then
        return string.char(f(n / 64) + 192, n % 64 + 128)
      elseif n <= 0xffff then
        return string.char(f(n / 4096) + 224, f(n % 4096 / 64) + 128, n % 64 + 128)
      elseif n <= 0x10ffff then
        return string.char(f(n / 262144) + 240, f(n % 262144 / 4096) + 128,
                           f(n % 4096 / 64) + 128, n % 64 + 128)
      end
      error( string.format("invalid unicode codepoint '%x'", n) )
    end
    '''
    def parse_unicode_escape(s):
        n1 = int(s[2:6], 16)
        return codepoint_to_utf8(n1)

        
    def parse_string(string, i):
        i += 1
        j = string.find('"', i)
        while string[j - 1] == '\\':
            j = string.find('"', j + 1)
        return string[i : j], j + 1
        #return string[i : j].replace('\\"', '"').replace('\\\\', '\\'), j + 1
        
        
    '''
    def parse_string(string, i):
        has_unicode_escape = False
        has_surrogate_escape = False
        has_escape = False
        last = None
        for j in range(i + 1, len(string)):
            x = ord(string[j])
            
            if x < 32:
                decode_error(string, j, "control character in string")
                
            if last == 92: # "\\" (escape char)
                if x == 117: # "u" (unicode escape sequence)
                    hex = string[j + 1, j + 5]
                    # if not hex:find("%x%x%x%x") then
                        # decode_error(string, j, "invalid unicode escape in string")
                    if hex:find("^[dD][89aAbB]") then
                        has_surrogate_escape = true
                    else
                        has_unicode_escape = true
            
                else
                    c = string[j]
                    if not escape_chars[c]:
                        decode_error(string, j, "invalid escape char '" + c + "' in string")
                    has_escape = True
                last = None

            elif x == 34: # '"' (end of string)
                s = string[i + 1: j - 1]
                # if has_surrogate_escape then 
                    # s = s:gsub("\\u[dD][89aAbB]..\\u....", parse_unicode_escape)
                # if has_unicode_escape then 
                    # s = s:gsub("\\u....", parse_unicode_escape)
                # if has_escape then
                    # s = s:gsub("\\.", escape_char_map_inv)
                return s, j + 1
        
            else
                last = x
        decode_error(string, i, "expected closing quote for string")
    '''
        
        
    '''
    local function parse_string(str, i)
      local has_unicode_escape = false
      local has_surrogate_escape = false
      local has_escape = false
      local last
      for j = i + 1, #str do
        local x = str:byte(j)

        if x < 32 then
          decode_error(str, j, "control character in string")
        end

        if last == 92 then # "\\" (escape char)
          if x == 117 then # "u" (unicode escape sequence)
            local hex = str:sub(j + 1, j + 5)
            if not hex:find("%x%x%x%x") then
              decode_error(str, j, "invalid unicode escape in string")
            end
            if hex:find("^[dD][89aAbB]") then
              has_surrogate_escape = true
            else
              has_unicode_escape = true
            end
          else
            local c = string.char(x)
            if not escape_chars[c] then
              decode_error(str, j, "invalid escape char '" .. c .. "' in string")
            end
            has_escape = true
          end
          last = nil

        elseif x == 34 then # '"' (end of string)
          local s = str:sub(i + 1, j - 1)
          if has_surrogate_escape then 
            s = s:gsub("\\u[dD][89aAbB]..\\u....", parse_unicode_escape)
          end
          if has_unicode_escape then 
            s = s:gsub("\\u....", parse_unicode_escape)
          end
          if has_escape then
            s = s:gsub("\\.", escape_char_map_inv)
          end
          return s, j + 1
        
        else
          last = x
        end
      end
      decode_error(str, i, "expected closing quote for string")
    end
    '''

    def parse_number(string, i):
        x = find_delim_chars(string, i).end()
        s = string[i : x]
        if '.' in s:
            return float(s), x
        else:
            return int(s), x
        

    def parse_literal(string, i):
        x = find_delim_chars(string, i).end()
        s = string[i: x]
        return literal_table[s], x
        
    '''
    local function parse_literal(str, i)
      local x = next_char(str, i, delim_chars)
      local word = str:sub(i, x - 1)
      if not literals[word] then
        decode_error(str, i, "invalid literal '" .. word .. "'")
      end
      return literal_table[word], x
    end
    '''
    
    if not array_creator:
        def array_creator(items):
            return list(items)
        
    def parse_array(string, i, _ws=" \t\r\n"):
        i += 1
        
        # skip whitespace
        try:
            nextchar = string[i]
            if nextchar in _ws:
                i = fint_not_space_chars(string, i).end()
                nextchar = string[i]
        except IndexError:
            nextchar = ''
        
        # meet empty array
        if nextchar == ']':
            return [], i + 1
        elif nextchar == '':
            decode_error(string, i, "Expecting value or ']'")
                
        def array_generator():
            nonlocal nextchar
            nonlocal i
            
            while 1:
                # Read token
                x, i = parse_dispatch_table[nextchar](string, i)
                yield x
                
                # skip whitespace
                try:
                    nextchar = string[i]
                    if nextchar in _ws:
                        i = fint_not_space_chars(string, i).end()
                        nextchar = string[i]
                except IndexError:
                    nextchar = ''
                    
                i += 1
                if nextchar == ']':
                    break
                elif nextchar != ',':
                    decode_error(string, i, "expected ']' or ','")

                # skip whitespace
                try:
                    nextchar = string[i]
                    if nextchar in _ws:
                        i += 1
                        nextchar = string[i]
                        if nextchar in _ws:
                            i = fint_not_space_chars(string, i).end()
                            nextchar = string[i]
                except IndexError:
                    nextchar = ''
         
        return array_creator(array_generator()), i
        
        
    if not object_creator:
        def object_creator(items):
            return dict(items)

    def parse_object(string, i, _ws=" \t\r\n"):
        i += 1
        
        # fast path
        nextchar = string[i]
        if nextchar != '"':
            if nextchar in _ws:
                i = fint_not_space_chars(string, i).end()
                nextchar = string[i]
            # empty object
            if nextchar == '}':
                return {}, i + 1
                
        def object_generator():
            nonlocal nextchar
            nonlocal i
            while 1:
                if nextchar != '"':
                    raise decode_error("Expecting property name enclosed in double quotes")
                    
                key, i = parse_string(string, i)
                
                # Read ':' delimiter
                if string[i] != ':':
                    i = fint_not_space_chars(string, i + 1).end()
                    if string[i] != ':':
                        decode_error(string, i, "expected ':' after key")
                        
                i += 1
                
                # # skip whitespace, fast path for `: ` or `:`
                try:
                    nextchar = string[i]
                    if nextchar in _ws:
                        i += 1
                        nextchar = string[i]
                        if nextchar in _ws:
                            i = fint_not_space_chars(string, i).end()
                            nextchar = string[i]
                except IndexError:
                    nextchar = ''
                
                # Read value
                val, i = parse_dispatch_table[nextchar](string, i)
                yield key, val
                
                # skip whitespace
                try:
                    nextchar = string[i]
                    if nextchar in _ws:
                        i = fint_not_space_chars(string, i).end()
                        nextchar = string[i]
                except IndexError:
                    nextchar = ''
                i += 1
                
                if nextchar == "}": break
                if nextchar != ",": decode_error(string, i, "expected '}' or ','")
                
                # skip whitespace
                try:
                    nextchar = string[i]
                    if nextchar in _ws:
                        i += 1
                        nextchar = string[i]
                        if nextchar in _ws:
                            i = fint_not_space_chars(string, i).end()
                            nextchar = string[i]
                except IndexError:
                    nextchar = ''

        return object_creator(object_generator()), i
        


    parse_dispatch_table = {
      '"' : parse_string,
      "0" : parse_number,
      "1" : parse_number,
      "2" : parse_number,
      "3" : parse_number,
      "4" : parse_number,
      "5" : parse_number,
      "6" : parse_number,
      "7" : parse_number,
      "8" : parse_number,
      "9" : parse_number,
      "-" : parse_number,
      "t" : parse_literal,
      "f" : parse_literal,
      "n" : parse_literal,
      "[" : parse_array,
      "{" : parse_object,
    }

    def parse(string, idx=0):
        idx = fint_not_space_chars(string, idx).end()
        c = string[idx]
        func  = parse_dispatch_table.get(c, None)
        if func:
            return func(string, idx)[0]
        decode_error(string,  idx, "unexpected character '" + c + "'")
        
    return parse
    
    
loads = parse = make_parse_functions()


# print(loads('[0,1,{"a": false, "b":null}, 1.0]'))


