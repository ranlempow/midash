from collections import namedtuple

class Pack:
    __slots__ = ['nexttime', 'every', 'func']
    def __init__(self, nexttime, every, func):
        self.nexttime = nexttime
        self.every = every
        self.func = func

frameCount = 0

class System1:
    THRESHOLD = 6
    debug = False
    
    def __init__(self):
        # called every frame
        self.tier0 = []
        # deadline < THRESHOLD frame
        self.tier1 = []
        # deadline >= THRESHOLD frame
        self.tier2 = []
        
'''
class System1:
    THRESHOLD = 6
    debug = False
    
    def __init__(self):
        # called every frame
        self.tier0 = []
        # deadline < THRESHOLD frame
        self.tier1 = []
        # deadline >= THRESHOLD frame
        self.tier2 = []
        
    def trigger(self, func, delay=0, every=0):
        pack = Pack(frameCount+delay, every, func)
        if every == 1:
            self.tier0.append(pack)
        elif delay < self.THRESHOLD:
            self.tier1.append(pack)
        else:
            self.tier2.append(pack)
        
    def iterTier0(self):
        for p in self.tier0:
            if p.nexttime <= frameCount:
                p.func()
        
    def iterTier1(self):
        _new_tier1 = []
        for p in self.tier1:
            if p.nexttime == frameCount:
                p.func()
                if p.every == 0:
                    continue
                p.nexttime = frameCount + p.every
                if p.every > self.THRESHOLD:
                    yield p
                    continue
            _new_tier1.append(p)
        self.tier1 = _new_tier1
        
    def iterTier2(self):
        _new_tier2 = []
        for p in self.tier2:
            if p.nexttime - frameCount < self.THRESHOLD:
                yield p
                continue
            _new_tier2.append(p)
        self.tier2 = _new_tier2

    
    def pump(self):
        global frameCount
        self.iterTier0()
        if frameCount % (self.THRESHOLD // 1) == 0:
            self.tier1.extend(self.iterTier2())
        self.tier2.extend(self.iterTier1())
        frameCount += 1
        
        if self.debug:
            print(callCount, len(self.tier0), len(self.tier1), len(self.tier2))

    
class System2(System1):
    def iterTier1(self):
        for p in self.tier1:
            if p.nexttime == frameCount:
                p.func()
                if p.every is None:
                    continue
                p.nexttime = frameCount + p.every
                if p.every > self.THRESHOLD:
                    self.tier2.append(p)
                    continue
            yield p
        
    def iterTier2(self):
        for p in self.tier2:
            if p.nexttime - frameCount < self.THRESHOLD:
                self.tier1.append(p)
                continue
            yield p
            
    def pump(self):
        global frameCount
        
        self.iterTier0()
        if frameCount % (self.THRESHOLD // 1) == 0:
            self.tier2 = list(self.iterTier2())
        self.tier1 = list(self.iterTier1())
        frameCount += 1
        if self.debug:
            print(callCount, len(self.tier0), len(self.tier1), len(self.tier2))
'''
    
    
    
class SystemCycle(System1):
    CYCLES = 64
    ROLLS = 8
    def __init__(self):
        self.tier0 = [ [[] for i in range(j+1)] for j in range(self.ROLLS) ]
        self.tier1 = [ [] for i in range(self.CYCLES) ]
        self.tier2 = []
        
        self._tierCache = [None] * (self.CYCLES)
        self.rotateCache()
        
    def rotateCache(self):
        for j in range(self.ROLLS):
            self._tierCache[j+1] = self.tier0[j][frameCount % (j+1)]
        self._tierCache[self.ROLLS+1:] = self.tier1[self.ROLLS+1:]
        
    def trigger(self, func, delay=0, every=0):
        self.process(delay, Pack(frameCount+delay, every, func))
        
    def process(self, delay, p):
        if delay == 0:
            self.fireNonTier0(p)
        if delay-1 < self.CYCLES:
            self.tier1[delay-1].append(p)
        else:
            self.tier2.append(p)
            
    def fireNonTier0(self, p):
        every = p.every
        p.func()
        if every == 0:
            pass
        elif every < self.CYCLES:
            self._tierCache[every].append(p)
        else:
            p.nexttime = frameCount + every
            self.tier2.append(p)
            
    def iterTier0(self):
        for j in range(self.ROLLS):
            for p in self.tier0[j][frameCount % (j+1)]:
                p.func()

    def iterTierCycle(self):
        self.rotateCache()
        for p in self.tier1[0]:
            self.fireNonTier0(p)
        self.tier1.pop(0)
        self.tier1.append([])
        
    def iterTier2(self):
        temp = self.tier2
        self.tier2 = []
        for p in temp:
            delay = p.nexttime - frameCount
            self.process(delay, p)
        
    def pump(self):
        global frameCount
        
        frameCount += 1
        
        self.iterTier0()
        self.iterTierCycle()
        if frameCount % self.CYCLES == 0:
            self.iterTier2()
        
        
        if self.debug:
            print(callCount, len(self.tier0[0][0]), len(self.tier0[1][0]), len(self.tier1[0]), len(self.tier2))

    
    
class SystemFool(System1):
    def trigger(self, func, delay=0, every=0):
        self.fire( Pack(frameCount+delay, every, func) )
        
    def fire(self, p):
        if p.nexttime == frameCount:
            p.func()
            if p.every == 0:
                return
            p.nexttime = frameCount + p.every
        self.tier0.append(p)
    
    def pump(self):
        global frameCount
        
        frameCount += 1
        
        temp = self.tier0
        self.tier0 = []
        for p in temp:
            self.fire(p)
        
        
        if self.debug:
            print(callCount, len(self.tier0))
            
        
        
        
        
callCount = 0
def _call():
    global callCount
    callCount += 1
    
# def _call():
    # pass
    
def test(systemClass=SystemCycle):
    global callCount
    system = systemClass()
    def _pump_count():
        system.pump()
        return callCount
    
    # ------------
    callCount = 0
    for i in range(3):
        system.trigger(_call, delay=1)
        system.trigger(_call, delay=2)
    assert( tuple(_pump_count() for i in range(4)) == (3,6,6,6) )
    
    # ------------
    
    callCount = 0
    for i in range(3):
        system.trigger(_call, delay=1, every=1)
    assert( tuple(_pump_count() for i in range(3)) == (3,6,9) )
    
    # ------------
    
    callCount = 0
    system = systemClass()
    system.trigger(_call, delay=1, every=1)
    system.trigger(_call, delay=2, every=1)
    system.trigger(_call, delay=3, every=1)
    assert( tuple(_pump_count() for i in range(4)) == (1,3,6,9) )

    # ------------
    
    callCount = 0
    system = systemClass()
    system.trigger(_call, delay=1, every=1)
    system.trigger(_call, delay=1, every=2)
    system.trigger(_call, delay=1, every=3)
    assert( tuple(_pump_count() for i in range(5)) == (3,4,6,8,10) )
    
    
    
    
    
def benchsetup(systemClass=SystemFool):
    global callCount
    callCount = 0
    
    system = systemClass()
    #system.debug = True
    for i in range(1000):
        system.trigger(_call, delay=i % 60, every=i % 15 + 1)
        
    for i in range(9000):
        system.trigger(_call, delay=i % 60, every=i % 300 + 1)
    return system
    
def benchmark(system):
    for i in range(1200):
        for i in range(50):
            system.trigger(_call, i % 30)
        system.pump()
        
    
    
if __name__ == '__main__':
    # import timeit
    # print(timeit.timeit('benchmark(system)', setup='from __main__ import benchsetup, benchmark, SystemFool; system=benchsetup(SystemFool)', number=1))
    # print(timeit.timeit('benchmark(system)', setup='from __main__ import benchsetup, benchmark, System1; system=benchsetup(System1)', number=1))
    # print(timeit.timeit('benchmark(system)', setup='from __main__ import benchsetup, benchmark, System2; system=benchsetup(System2)', number=1))
    # print(timeit.timeit('benchmark(system)', setup='from __main__ import benchsetup, benchmark, SystemCycle; system=benchsetup(SystemCycle)', number=1))
    
    # import cProfile
    # system = benchsetup(SystemCycle)
    # cProfile.run('benchmark(system)')
    
    test(SystemFool)
    # test(System1)
    # test(System2)
    test(SystemCycle)
    
    
        
    