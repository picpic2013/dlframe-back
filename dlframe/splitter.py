from typing import Tuple
from webitem import WebItem
from dataset import DataSet, ListDataSet

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
        self.ratio = ratio

    def split(self, dataset: DataSet) -> Tuple[DataSet, DataSet]:
        length = len(dataset)
        
        return (
            ListDataSet([dataset[i] for i in range(math.floor(length * self.ratio))]), 
            ListDataSet([dataset[i] for i in range(math.floor(length * self.ratio), length)])
        )