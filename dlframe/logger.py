from __future__ import annotations

class Logger:
    def __init__(self) -> None:
        pass

    def progess(self, percentage: float) -> Logger:
        return self

    def print(self, *params, end='\n') -> Logger:
        return self

class CmdLogger(Logger):
    def __init__(self, name=None) -> None:
        super().__init__()
        if name is None:
            name = 'untitled'
        self.name = name

    def progess(self, percentage: float) -> Logger:
        print('[{}]:'.format(self.name), 'now progress:', percentage)
        return super().progess(percentage)

    def print(self, *params, end='\n') -> Logger:
        print('[{}]:'.format(self.name), *params, end=end)
        return super().print(*params, end=end)