import re

class Token:
    int_re = re.compile(r'^[0-9]+$')
    def __init__(self, content=None, before='', tokens=None):
        self.before = before.replace('\\{', '{').replace('\\}', '}')
        self.children = tokens or []
        self.argidx = 9999
        self.attribute_default = 'NONE'
        self.attribute_access = []
        self.key = None
        if content:
            if content[0] == '$':
                content = content[1:]
                if '|' in content:
                    content, self.attribute_default = content.split('|')
                self.attribute_access = content.split('.')
            elif self.int_re.match(content):
                self.argidx = int(content)
            else:
                self.key = content
        
    def _format(self, context, args=[]):
        if self.argidx < len(args):
            return args[self.argidx].format(context)
        if self.attribute_access:
            node = context.attributes
            for attr in self.attribute_access:
                if isinstance(node, list):
                    if int(attr) >= len(node):
                        return elf.attribute_default
                    node = node[int(attr)]
                else:
                    if attr not in node:
                        return self.attribute_default
                    node = node[attr]
            
            return context.format(node)
        if self.key:
            return context.format(self.key)
        return ''
        
    def format(self, context, args=[]):
        after = ''.join(token.format(context, args) for token in self.children)
        return self.before + self._format(context, args) + after
        
class Context:
    split_re = re.compile(r'(?<!\\){([^}]|(?<=\\)})*}')
    def __init__(self):
        self.dict = {}
        self.cache = {}
        self.attributes = {}
        
    def parse(self, text):
        tokens, lastpos = [], 0
        for match in self.split_re.finditer(text):
            tokens.append(Token(match.group(0)[1:-1], text[lastpos:match.start()]))
            lastpos = match.end()
        tokens.append(Token(None, text[lastpos:]))
        return Token(tokens=tokens)
        
    def format(self, key, *args):
        args = [self.cache.setdefault(a, self.parse(a)) for a in args]
        token = self.dict.get(key, self.cache.setdefault(key, self.parse(key)))
        return token.format(self, args)
       
    def set(self, key, context):
        self.dict[key] = self.parse(context)
        