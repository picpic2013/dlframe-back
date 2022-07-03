from typing import Any
from webitem import WebItem
from dataset import DataSet

class Model(WebItem):
    def __init__(self) -> None:
        super().__init__()

    def train(self, trainDataset: DataSet) -> None:
        pass

    def test(self, testDataset: DataSet) -> Any:
        pass