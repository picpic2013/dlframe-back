from dlframe import WebManager, Logger

import math
import numpy as np

# 数据集
class TestDataset:
    def __init__(self, num) -> None:
        super().__init__()
        self.num = range(num)
        self.logger = Logger.get_logger('TestDataset')
        self.logger.print("I'm in range 0, {}".format(num))

    def __len__(self) -> int:
        return len(self.num)

    def __getitem__(self, idx: int):
        return self.num[idx]

class TrainTestDataset:
    def __init__(self, item) -> None:
        super().__init__()
        self.item = item

    def __len__(self) -> int:
        return len(self.item)

    def __getitem__(self, idx: int):
        return self.item[idx]

# 数据集切分器
class TestSplitter:
    def __init__(self, ratio) -> None:
        super().__init__()
        self.ratio = ratio
        self.logger = Logger.get_logger('TestSplitter')
        self.logger.print("I'm ratio:{}".format(self.ratio))

    def split(self, dataset):
        trainingSet = [dataset[i] for i in range(math.floor(len(dataset) * self.ratio))]
        trainingSet = TrainTestDataset(trainingSet)

        testingSet = [dataset[i] for i in range(math.floor(len(dataset) * self.ratio), len(dataset))]
        testingSet = TrainTestDataset(testingSet)

        self.logger.print("split!")
        self.logger.print("training_len = {}".format([trainingSet[i] for i in range(len(trainingSet))]))
        return trainingSet, testingSet

# 模型
class TestModel:
    def __init__(self, learning_rate) -> None:
        super().__init__()
        self.learning_rate = learning_rate
        self.logger = Logger.get_logger('TestModel')

    def train(self, trainDataset) -> None:
        self.logger.print("trainging, lr = {}, trainDataset = {}".format(self.learning_rate, trainDataset))

    def test(self, testDataset):
        self.logger.print("testing")
        self.logger.imshow(np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8))
        return testDataset

# 结果判别器
class TestJudger:
    def __init__(self) -> None:
        super().__init__()
        self.logger = Logger.get_logger('TestJudger')

    def judge(self, y_hat, test_dataset) -> None:
        self.logger.print("y_hat = {}".format([y_hat[i] for i in range(len(y_hat))]))
        self.logger.print("gt = {}".format([test_dataset[i] for i in range(len(test_dataset))]))

if __name__ == '__main__':
    with WebManager() as manager:

        dataset = manager.register_element('数据集', {'10_nums': TestDataset(10), '20_nums': TestDataset(20)})
        splitter = manager.register_element('数据分割', {'ratio:0.8': TestSplitter(0.8), 'ratio:0.5': TestSplitter(0.5)})
        model = manager.register_element('模型', {'model1': TestModel(1e-3)})
        judger = manager.register_element('评价指标', {'judger1': TestJudger()})

        train_data_test_data = splitter.split(dataset)
        train_data, test_data = train_data_test_data[0], train_data_test_data[1]
        model.train(train_data)
        y_hat = model.test(test_data)
        judger.judge(y_hat, test_data)