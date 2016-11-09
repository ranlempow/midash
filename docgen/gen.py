import os
import os.path as path
import sys
import imp
import re

import pdoc
import inspect

from mako.lookup import TemplateLookup

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '../midash')))
pdoc.tpl_lookup = TemplateLookup(
                            directories=path.dirname(__file__),
                            cache_args={'cached': True,
                                        'cache_type': 'memory'})
        

class MidashModule:
    def __init__(self, package):
        import midash
        from midash import _
        
        self.methods = {}
        _.require(package, _debug=True)
        for methods in midash._debug_mixin_observer.values():
            for method in methods:
                self.methods[method.name] = method
                


_cleandoc = inspect.cleandoc
def cleandoc(docstring):
    docstring = _cleandoc(docstring)
    # support converting docstring to code
    _lines = docstring.split('\n')
    _newlines = []
    _into = []
    for i, ln in enumerate(_lines):
        if ln.startswith('>>>') or (i > 0 and _lines[i-1].startswith('>>>')):
            ln = ' ' * 4 + ln
            _into.append(i)
            if (i - 1) not in _into:
                _newlines.append('')
        _newlines.append(ln)
    return '\n'.join(_newlines)
    
inspect.cleandoc = cleandoc

class pModule(pdoc.Module):
    def mro(self, cls):
        # no mro detect
        return []

    def descendents(self, cls):
        # no descendents detect
        return []


# Get the module that we're documenting. Accommodate for import paths,
# files and directories.
def getMoudle(package):
    module_path = path.join(path.dirname(__file__), '..', 'midash', package + '.py')
    fp = path.realpath(module_path)
    with open(fp, encoding='utf-8') as f:
        module = imp.load_source(package, fp, f)

    return pModule(module, docfilter=None, allsubmodules=False), MidashModule(package.strip('_'))

def make_markdown(packages):
    modules = []
    all_items = {}
    for package in packages:
        module, midash_module = getMoudle(package)

        items = []
        for getter in [module.functions, module.variables, module.classes]:
            for d in getter():
                if d.name in midash_module.methods:
                    d.mi_method = midash_module.methods[d.name]
                    items.append(d)
                    all_items[d.name] = d
                    
        modules.append({
                "name": package.strip('_'),
                "module": module,
                "items": items
        })
    
    # Plain text
    t = pdoc._get_tpl('text.mako')
    text, _ = re.subn('\n\n\n+', '\n\n', t.render(modules=modules, all_items=all_items).strip())
    try:
        print(text)
        pass
    except IOError as e:
        # This seems to happen for long documentation.
        # This is obviously a hack. What's the real cause? Dunno.
        if e.errno == 32:
            pass
        else:
            raise e
    return
    
make_markdown(['lang', 'math_'])

