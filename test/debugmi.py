import os
import sys
sys.path.insert(0, os.path.abspath('../midash'))

import midash
from midash import _

def show(package):
    _.require(package, _debug=True)
    observer = midash._debug_mixin_observer[_]
    print('package {}: {} defines in TopLevel'.format(package, len(observer)))
    print('-----------------------')
    for m in sorted(observer, key=lambda m: m.name):
        print('{:15s} {}'.format(m.name, m.shortdesc[:60]))

show('lang')