from dlframe import CalculationNodeManager
from dlframe import Logger


class A:
    def __init__(self, name) -> None:
        self.name = name
        self.logger = Logger.get_logger('a')

    def f(self, a):
        return a + self.name
    
    def print(self, x):
        # print(x)
        self.logger.print(x)

def fsdfs(a, b):
    return a + b

if __name__ == '__main__':
    
    a1 = A('a1')
    a2 = A('a2')

    manager = CalculationNodeManager()

    m = manager.register_element('m', {
        'a1': A, 
        'a2': A
    })

    b = manager.register_element('b', {
        'b1': fsdfs
    })

    cc = manager.register_element('c', {
        's1': 's1', 
        's2': 's2', 
        's3': 's3', 
    })

    a = m(cc)
    tmp = a.f(cc)
    a.print(tmp)
    tmp2 = a.f('aaaa')
    a.print(b(a.name, a.name))

    # manager.execute({
    #     'a': 'a2'
    # })

    print(manager.inspect())

    manager.execute({
        'm': 'a1', 
        'c': 's1'
    })

    print(a1)
