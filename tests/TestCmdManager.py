import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(
        os.path.abspath(__file__), '..', '..'
    )
))

from dlframe import CmdManager, DataSet, DirectSplitter, Model, Judger
from typing import Any

class DebugDataset(DataSet):
    def __init__(self, number) -> None:
        super().__init__()
        self.numbers = list(range(number))

    def __len__(self) -> int:
        return len(self.numbers)

    def __getitem__(self, idx: int) -> int:
        return self.numbers[idx]

class DebugModel(Model):
    def __init__(self) -> None:
        super().__init__()

    def train(self, trainDataset: DataSet) -> None:
        self.logger.print('training...')
        self.logger.print('we have trainging input', [trainDataset[_] for _ in range(len(trainDataset))])
        return super().train(trainDataset)

    def test(self, testDataset: DataSet) -> Any:
        self.logger.print('testing...')
        self.logger.print('we have testing input', [testDataset[_] for _ in range(len(testDataset))])
        return [testDataset[_] for _ in range(len(testDataset))]

class DebugJudger(Judger):
    def __init__(self) -> None:
        super().__init__()

    def judge(self, y_hat, test_dataset: DataSet) -> None:
        self.logger.print('judging')
        self.logger.print('y_hat is', y_hat)
        self.logger.print('test_dataset is', [test_dataset[_] for _ in range(len(test_dataset))])
        return super().judge(y_hat, test_dataset)

if __name__ == '__main__':
    manager = CmdManager()

    manager.register_dataset(
        DebugDataset(10)
    ).register_splitter(
        DirectSplitter(0.2)
    ).register_model(
        DebugModel()
    ).register_judger(
        DebugJudger()
    ).start()