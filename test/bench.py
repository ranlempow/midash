import os
import sys
from benchtool import setup
sys.path.insert(0, os.path.abspath('../midash'))

    
def _py_setup(number=10000, inner=50, size=50):
    return (inner, [list(range(size)) for i in range(number)])
    
def _it_setup(number=10000, inner=50, size=50):
    from midash import _
    _.require('iterators')
    _.require('_faster_iter')
    return (inner, _, [_.triplize(tuple(range(size))) for i in range(number)])
    
def _it_setup_nt(number=10000, inner=50, size=50):
    from midash import _
    _.require('iterators')
    _.require('_faster_iter')
    return (inner, _, [list(range(size)) for i in range(number)])
    

    
@setup(_py_setup)
def py_append(inner, pool):
    def run():
        for a in pool:
            for i in range(inner):
                a.pop(0)
            for v in a:
                pass
        return a
    return run

@setup(_py_setup)
def py_insert(inner, pool):
    def run():
        for a in pool:
            for i in range(inner):
                a.insert(0, -i)
            for v in a:
                pass
        return a
    return run
    
@setup(_py_setup)
def py_array1(inner, pool):
    def run():
        for a in pool:
            for i in range(inner):
                a = a[1:]
        return a
    return run
    
@setup(_py_setup)
def py_array_add(inner, pool):
    def run():
        for a in pool:
            for i in range(inner):
                a = [i] + a
        return a
    return run
    
@setup(_it_setup)
def dash_insert(inner, _, pool):
    def run():
        for a in pool:
            a = _.insert_(a, 0, _.range(-inner-1, 0, 1))
            for v in a:
                pass
        return a
    return run
    
@setup(_it_setup)
def dash_insertF(inner, _, pool):
    def run():
        for a in pool:
            a = _.insertF(a, 0, _.range(-inner-1, 0, 1))
            for v in a:
                pass
        return a
    return run
    
@setup(_it_setup_nt)
def dash_insert_notri(inner, _, pool):
    def run():
        for a in pool:
            a = _.insert_nt(a, 0, _.range_nt(-inner-1, 0, 1))
            for v in a:
                pass
        return a
    return run
    
@setup(_it_setup)
def dash_range(inner, _, pool):
    def run():
        for a in pool:
            #a = _.triplize(tuple(range(-49, 0, 1)))
            a = _.range(-inner-1, 0, 1)
            a = list(a)
        return a
    return run
    
@setup(_it_setup)
def dash_clear(inner, _, pool):
    def run():
        for a in pool:
            # for i in range(inner):
                # a = _.removeAt_(a, 0)
            a = _.clear_(a)
            for v in a:
                pass
        return a
    return run
    

suit1 = {
    'benchs': [
        py_append,
        py_insert,
        py_array1,
        py_array_add,
        dash_insert,
        dash_insertF,
        dash_insert_notri,
        dash_range,
        dash_clear
    ],
    'params': [
        (10000, 50, 50),
        (10000, 20, 50),
        (10000,  5, 50),
        (10000,  5,  5),
    ]
}



