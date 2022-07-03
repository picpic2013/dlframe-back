from typing import Any
from webitem import WebItem
from dataset import DataSet

class Model(WebItem):
    def __init__(self) -> None:
        super().__init__()

    def train(trainDataset: DataSet) -> Any:
        pass

    def test(testDataset: DataSet) -> Any:
        pass