from __future__ import annotations
import time
from typing import Any, Callable, Union

class PICTimerWith:
    def __init__(self, name=None, showTimeWhenRunning=False, autoStart=False) -> None:
        '''
        @param name:                timer name ('untitled' in default)
        @param showTimeWhenRunning: whether enable print before summary
               Note that printing the results before the summary will 
               reduce the time measurement accuracy
        '''
        if name is None:
            name = 'untitled'
        self.__timer_name = name
        self.__showCount = 0
        self.__intervalTimes = []
        self.__startTime = None
        
        self.__results = []
        self.__showTimeWhenRunning = showTimeWhenRunning

        self.__subTimers = []
        
        if autoStart:
            self.startTimer()

    def __printToResults(self, *content, end='\n'):
        if self.__showTimeWhenRunning:
            print(*content, end=end)
        else:
            self.__results.append((content, end))
            # self.__results.append(''.join(content) + end)

    def showTime(self, name=None, forcePrint=False) -> PICTimerWith:
        '''
        log time
        @param name:       time point name ('stage_%d' in default)
        @param forcePrint: whether print immediately (SLOW)
        @returns:          the timer
        '''
        assert self.__startTime is not None, 'you should call ${timer_name}.startTimer() first!'

        if name is None:
            name = 'stage_%d' % (self.__showCount)
        
        endTime = time.time()
        self.__printToResults("\033[32m[ {}.{} ] excution time(from begin): \033[31m{:.4f} ms\033[0m".format(self.__timer_name, name, (endTime - self.__startTime) * 1000), end='')
        if self.__showCount > 0:
            self.__printToResults(", \033[32m[ {}.{} ] excution time(from last): \033[31m{:.4f} ms\033[0m".format(self.__timer_name, name, (endTime - self.__intervalTimes[-1]) * 1000))
        else:
            self.__printToResults()
        self.__intervalTimes.append(endTime)
        self.__showCount += 1

        if forcePrint:
            self.forceShowTime()

        return self
    
    def forceShowTime(self) -> PICTimerWith:
        '''
        show time immediately
        Note that this function will reduce the time measurement accuracy
        Do NOT use this function in ANY time sensitive situation!
        '''
        for c, e in self.__results:
            print(*c, end=e)
        self.__results.clear()
        return self

    def startTimer(self) -> PICTimerWith:
        '''
        start the timer
        '''
        assert self.__startTime is None, 'the timer is already started!'
        self.__startTime = time.time()
        self.__intervalTimes.append(self.__startTime)
        return self

    def summary(self) -> PICTimerWith:
        '''
        quit the timer and show results
        '''

        assert self.__startTime is not None, 'you should call ${timer_name}.startTimer() first!'

        for subTimer in self.__subTimers:
            subTimer.summary()

        self.showTime('total' if self.__showCount == 0 else 'last')
        if len(self.__intervalTimes) > 2:
            deltaTimes = [j - i for i, j in zip(self.__intervalTimes, self.__intervalTimes[1:])]
            self.__printToResults("\033[32m[ {}.{} ] excution time: \033[31m{:.4f} ms\033[0m".format(self.__timer_name, 'mean', sum(deltaTimes) * 1000 / len(deltaTimes)))
        self.__printToResults()

        if not self.__showTimeWhenRunning:
            self.forceShowTime()
        return self

    def __enter__(self) -> PICTimerWith:
        return self.startTimer()

    def __exit__(self, type, value, trace):
        self.summary()

    def getTimer(self, name=None, showTimeWhenRunning=False, autoStart=False) -> PICTimerWith:
        if name is None:
            name = 'untitled'
        subTimer = PICTimerWith(self.__timer_name + '.' + name, showTimeWhenRunning=showTimeWhenRunning, autoStart=autoStart)
        self.__subTimers.append(subTimer)
        return subTimer

def makePICTimerWrapper(func) -> Union[Callable, PICTimer]:
    return func

@makePICTimerWrapper
class PICTimer:
    def __init__(self, func: Callable) -> None:
        self.func = func

    def call(self, *args: Any, **kwargs: Any) -> Any:
        assert self.func is not None, 'function is None'

        with PICTimer.getTimer(self.func.__name__):
            res = self.func(*args, **kwargs)
        return res

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.call(*args, **kwds)

    @staticmethod
    def getTimer(name=None, showTimeWhenRunning=False, autoStart=False) -> PICTimerWith:
        return PICTimerWith(name, showTimeWhenRunning=showTimeWhenRunning, autoStart=autoStart)


# examples
if __name__ == '__main__':
    # example 1
    # function timer
    print('='*50, 'example 1', '='*50)
    @PICTimer
    def f1():
        for _ in range(100000):
            b = _

    f1()

    # example 2
    # with code block
    print('='*50, 'example 2', '='*50)
    with PICTimer.getTimer('example2') as t:
        for _ in range(1, 100000):
            if _ % 20000 == 0:
                t.showTime()
            bb = _

    # example 3
    print('='*50, 'example 3', '='*50)
    timer = PICTimer.getTimer('example3') # -┬--> or `timer = PICTimer.getTimer('example3', autoStart=True)`
    timer.startTimer()                    # -┘
    for idx in range(3):
        for _ in range(1, 100000):
            if _ % 20000 == 0:
                timer.showTime("stage_" + str(_))
            bb = _
        timer.forceShowTime() # you can output results before summary
    timer.summary()

    # example 4
    # create sub-timer
    print('='*50, 'example 4', '='*50)
    timer = PICTimer.getTimer('example4', autoStart=True)
    for idx in range(3):
        subTimer = timer.getTimer('sub_' + str(idx), autoStart=True)
        for _ in range(1, 100000):
            if _ % 20000 == 0:
                subTimer.showTime("stage_" + str(_))
            bb = _
        timer.showTime()
    timer.summary()