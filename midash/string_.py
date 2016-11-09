
# lua regex library
# http://apostata.web.fc2.com/luaregex/index-en.html
def _compile(pattern):
    import re
    return re.compile(pattern)

# String
def match(string, pattren):
    m = pattern.fullmatch(string)
    return m is not None
    
# String
def search(string, pattern, start=None, end=None):
    pattern = _compile(pattren)
    m = pattern.search(string, start, end)
    if not m:
        return -1
    return m.start()
    
# String
def findall(string, pattern, start=None, end=None):
    pattern = _compile(pattren)
    for m in pattern.finditer(string, start, end):
        yield m.group()
        
# String
def replace(string, pattern, replaced, count=0):
    pattern = _compile(pattren)
    return m.sub(replaced, string, count)
    
# String
def split(string, pattern, maxsplit=0):
    pattern = _compile(pattern)
    for m in split(string, maxsplit):
        yield m

