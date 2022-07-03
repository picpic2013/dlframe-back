from dlframe.webitem import WebItem
from dlframe.dataset import DataSet

class Judger(WebItem):
    def __init__(self) -> None:
        super().__init__()

    def judge(self, y_hat, test_dataset: DataSet) -> None:
        pass