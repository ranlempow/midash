#from midash import _

def a():
    return 'im a'
    
def setup(_):
    _.mixin({'a': a})
    