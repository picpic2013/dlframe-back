from typing import Callable
from functools import reduce, wraps

def decohints(decorator: Callable) -> Callable:
    return decorator

def isTheSameType(last, now):
    '''
    @param last: (lastRes, lastType)
        lastRes: None | are previous elements same type
        lastType: type of the last element

    @param now:  current element
    @returns:  (lastRes, lastType)
    '''
    lastRes, lastType = last
    return (lastType is None or (lastRes and (lastType == type(now))), type(now))

@decohints
def make_recursive_func(func: Callable) -> Callable:
    """Convert a function into recursive style to handle nested dict/list/tuple variables

    Args:
        func: input function
        func Args: 
            vars:   element / list / tuple / dict
            args:   other arguments
            kwargs: other keyword arguments

    Returns:
        recursive style function
    """

    def tupleGeneration(*args, **kwargs):
        for arg in zip(*args):
            yield wrapper(*arg, **kwargs)

    @wraps(func)
    def wrapper(*args, **kwargs):
        eleEq, eleType = reduce(isTheSameType, args, (True, None))
        if eleEq:
            if eleType == list:
                return [wrapper(*arg, **kwargs) for arg in zip(*args)]
            elif eleType == tuple or eleType == type(tupleGeneration()):
                return tupleGeneration(*args, **kwargs)
            elif eleType == dict:
                resDict = {}
                for arg in args:
                    for k, v in arg.items():
                        resDict.setdefault(k, [])
                        resDict[k].append(v)
                return {k:wrapper(*v, **kwargs) for k, v in resDict.items()}
        return func(*args, **kwargs)
    return wrapper

@decohints
def make_multi_return_recursive_func(func: Callable) -> Callable:
    """Convert a function into recursive style to handle nested dict/list/tuple variables
    that returns multiple results
    WARNING! tuple is treated the same as list

    Args:
        func: input function
        func Args: 
            vars:   element / list / tuple / dict
            args:   other arguments
            kwargs: other keyword arguments

    Returns:
        recursive style function
    """

    def tupleGeneration(*args, **kwargs):
        for arg in zip(*args):
            yield wrapper(*arg, **kwargs)

    @wraps(func)
    def wrapper(*args, **kwargs):
        eleEq, eleType = reduce(isTheSameType, args, (True, None))
        if eleEq:
            if eleType == list or (eleType == tuple or eleType == type(tupleGeneration())):
                tempReturn = [wrapper(*arg, **kwargs) for arg in zip(*args)]
                returnResults = None
                for item in tempReturn:
                    if returnResults is None:
                        returnResults = [[_] for _ in item]
                    else:
                        assert len(returnResults) == len(item), 'the function must have the same number of the return value'
                        for oldResult, newResult in zip(returnResults, item):
                            oldResult.append(newResult)
                return returnResults
            elif eleType == dict:
                resDict = {}
                for arg in args:
                    for k, v in arg.items():
                        resDict.setdefault(k, [])
                        resDict[k].append(v)
                tempReturn = {k:wrapper(*v, **kwargs) for k, v in resDict.items()}
                returnResults = None
                for key, item in tempReturn.items():
                    if returnResults is None:
                        returnResults = [{key: value} for value in item]
                    else:
                        assert len(returnResults) == len(item), 'the function must have the same number of the return value'
                        for oldResult, newValue in zip(returnResults, item):
                            oldResult.setdefault(key, newValue)
                return returnResults

        return func(*args, **kwargs)
        
    return wrapper

if __name__ == '__main__':
    # dict args
    arg1 = {idx: 'arg1_k_'+str(idx) for idx in range(3)}
    arg2 = {idx: 'arg2_k_'+str(idx) for idx in range(3)}
    
    # list args
    arg1 = [_ for _ in range(10)]
    arg2 = [_ for _ in range(10)]

    # tuple / generator args
    arg1 = (_ for _ in range(10))
    arg2 = (_ for _ in range(10))

    # non-iterable args
    arg1 = 0
    arg2 = 1

    # mutiple args
    arg1 = {idx: ['arg1_k_'+str(idx)+'_l_'+str(_) for _ in range(2)] for idx in range(3)}
    arg2 = {idx: ['arg2_k_'+str(idx)+'_l_'+str(_) for _ in range(2)] for idx in range(3)}

    @make_recursive_func
    def f1(x, base):
        return base.format(x)

    @make_recursive_func
    def f2(x, y, base):
        return base.format(x, y)

    @make_recursive_func
    def f3(x, y, base1, base2):
        return base1.format(x), base2.format(y)

    @make_multi_return_recursive_func
    def f4(x, y, base1, base2):
        return base1.format(x), base2.format(y)

    res1 = f1(arg1, base="arg1: {}")
    res2 = f2(arg1, arg2, base="arg1: {}, arg2: {}")
    res3 = f3(arg1, arg2, base1="arg1: {}", base2=" arg2: {}")
    res4 = f4(arg1, arg2, base1="arg1: {}", base2=" arg2: {}")

    print(res1)
    print(res2)
    print(res3)
    print(res4)
    print()