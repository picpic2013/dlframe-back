from typing import Tuple
from dlframe.webitem import WebItem
from dlframe.dataset import DataSet, ListDataSet

import math

class Splitter(WebItem):
    def __init__(self) -> None:
        super().__init__()

    # training data, test data
    def split(self, dataset: DataSet) -> Tuple[DataSet, DataSet]:
        pass

class DirectSplitter(Splitter):
    def __init__(self, ratio) -> None:
        super().__init__()
        self.ratio = float(ratio)

    def split(self, dataset: DataSet) -> Tuple[DataSet, DataSet]:
        length = len(dataset)
        
        return (
            ListDataSet([dataset[i] for i in range(math.floor(length * self.ratio))]), 
            ListDataSet([dataset[i] for i in range(math.floor(length * self.ratio), length)])
        )