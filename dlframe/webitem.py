from dlframe.logger import Logger

class WebItem:
    logger: Logger

    def __init__(self) -> None:
        self.logger = Logger()