from __future__ import annotations

class Logger:
    def __init__(self) -> None:
        self.aa = 0
        pass

    def progess(self, percentage: float) -> Logger:
        return self

    def print(self, *params, end='\n') -> Logger:
        return self