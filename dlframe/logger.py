class Logger:
    def __init__(self, name, trigger=None) -> None:
        self.name = name
        self.trigger = trigger

    def print(self, *x, **kwargs):
        if self.trigger is not None:
            self.trigger({
                'type': 'print', 
                'name': self.name, 
                'args': x, 
                'kwargs': kwargs
            })
            return
        print('[{}]: '.format(self.name), end=' ')
        print(*x, **kwargs)

    def imshow(self, img):
        if self.trigger is not None:
            self.trigger({
                'type': 'imshow', 
                'name': self.name, 
                'args': img
            })
            return
        print(img)

    @classmethod
    def get_logger(cls, name):
        logger = cls(name)
        cls.loggers.setdefault(id(logger), logger)
        return logger

Logger.loggers = {}