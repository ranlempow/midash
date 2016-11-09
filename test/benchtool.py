'''
Exampe:

def bench_1(n=10):
    a = []
    a.extend(range(n))
    
    def run():
        b = a[:]
        
    return run
    
suit_1 = {
    'benchs': [bench_1, bench_1],
    'params': [(10,), (2000,)],
}
'''

import timeit
import cProfile
from functools import wraps

def setup(setupfunc):
    def chained(func):
        @wraps(func)
        def f(*args):
            passing = setupfunc(*args)
            return func(*passing)
        return f
    return chained
    
    
def benchmark(module_path, target=None, profile=False):
    import importlib
    if target is None:
        module_path, target = module_path.split('.')
    module = importlib.import_module(module_path, package=None)
    target = getattr(module, target)
    if callable(target):
        benchs = [target]
        params = [()]
    elif isinstance(target, dict) and 'benchs' in target:
        benchs = [ b for b in target['benchs'] ]
        params = target['params'] if 'params' in target else [()]
        
        
    print()
    print('Parameters:')
    for i, param in enumerate(params):
        print('{} = {}'.format(i, repr(param)))
        
    if profile:
        run = benchs[0]()
        cProfile.runctx('run()', {'run':run}, {})
    else:
        print(('{:20s}' + '{:9d}' * len(params)).format('', *range(1, len(params) + 1)))
        for func in benchs:
            result = []
            for param in params:
                t = timeit.timeit(
                        'run()','from {0} import {1}; run = {1}({2})'.format(
                            module_path, 
                            func.__name__,
                            ','.join(repr(p) for p in param)
                        ), number=1)
                result.append(t)
                
            print(('{:20s}' + '{:9.6f}' * len(params)).format(func.__name__, *result))
            
            
if __name__ == '__main__':
    import sys
    profile = False
    if '--profile' in sys.argv:
        profile = True
        sys.argv.remove('--profile')
        
    if len(sys.argv) == 2:
        benchmark(sys.argv[1], profile=profile)
    elif len(sys.argv) == 3:
        benchmark(sys.argv[1], sys.argv[2], profile=profile)
    else:
        assert( False )
        