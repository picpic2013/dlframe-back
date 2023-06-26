from dlframe import WebManager, Logger

import numpy as np

class A:
    def __init__(self, name) -> None:
        self.name = name
        self.logger = Logger.get_logger('A')

    def f(self, a):
        return a + self.name
    
    def print(self, x):
        # print(x)
        self.logger.print(x)

        image_np = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        self.logger.imshow(image_np)

def fsdfs(a, b):
    return a + b

if __name__ == '__main__':

    with WebManager() as manager:

        a = manager.register_element('a', {
            'a1': A('a1'), 
            'a2': A('a2')
        })

        b = manager.register_element('b', {
            'b1': fsdfs
        })

        cc = manager.register_element('c', {
            's1': 's1', 
            's2': 's2', 
            's3': 's3', 
        })

        tmp = a.f(cc)
        a.print(tmp)
        # tmp2 = a.f('aaaa')
        # a.print(b(a.name, a.name))