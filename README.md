# DL-Frame

一个及其简易的机器学习可视化框架，用户仅需实现：
- 数据载入逻辑
- 数据集分割逻辑
- 模型训练逻辑
- 模型测试逻辑
- 结果判别逻辑

即可将自定义类注册进 Manager 运行。

--- 

框架提供了 logger，开发者可以方便地向前端输出内容。

--- 

核型运行逻辑：

~~~python
train_data, test_data = splitter.split(dataset)
model.train(train_data)
y_hat = model.test(test_data)
judger.judge(y_hat, test_data)
~~~

--- 

本框架仅提供 WebSocket 服务，不提供页面显示。需配合[前端](https://dlframe.picpic.site/)使用。前端代码开源在[仓库](https://github.com/picpic2013/dlframe-front.git)。

## 安装方法

~~~bash
# 可选，新建 conda 环境
conda create -n dlframe python=3.8
conda activate dlframe

# 克隆仓库与安装
git clone https://github.com/picpic2013/dlframe-back.git
cd dlframe-back
python ./setup.py install
~~~

## 测试用例

~~~bash
python tests/Display.py
~~~

## 使用示例

仅需实现以下接口，即可将自定义类注册进 Manager 运行

~~~python
from dlframe import DataSet, Splitter, Model, Judger, WebManager

# 数据集
class TestDataset(DataSet):
    def __init__(self, num) -> None:
        super().__init__()
        self.num = range(num)
        self.logger.print("I'm in range 0, {}".format(num))

    def __len__(self) -> int:
        return len(self.num)

    def __getitem__(self, idx: int) -> Any:
        return self.num[idx]

class TrainTestDataset(DataSet):
    def __init__(self, item) -> None:
        super().__init__()
        self.item = item

    def __len__(self) -> int:
        return len(self.item)

    def __getitem__(self, idx: int) -> Any:
        return self.item[idx]

# 数据集切分器
class TestSplitter(Splitter):
    def __init__(self, ratio) -> None:
        super().__init__()
        self.ratio = ratio
        self.logger.print("I'm ratio:{}".format(self.ratio))

    def split(self, dataset: DataSet) -> Tuple[DataSet, DataSet]:
        trainingSet = [dataset[i] for i in range(math.floor(len(dataset) * self.ratio))]
        trainingSet = TrainTestDataset(trainingSet)

        testingSet = [dataset[i] for i in range(math.floor(len(dataset) * self.ratio), len(dataset))]
        testingSet = TrainTestDataset(testingSet)

        self.logger.print("split!")
        self.logger.print("training_len = {}".format([trainingSet[i] for i in range(len(trainingSet))]))
        return trainingSet, testingSet

# 模型
class TestModel(Model):
    def __init__(self, learning_rate) -> None:
        super().__init__()
        self.learning_rate = learning_rate

    def train(self, trainDataset: DataSet) -> None:
        self.logger.print("trainging, lr = {}".format(self.learning_rate))
        return super().train(trainDataset)

    def test(self, testDataset: DataSet) -> Any:
        self.logger.print("testing")
        return testDataset

# 结果判别器
class TestJudger(Judger):
    def __init__(self) -> None:
        super().__init__()

    def judge(self, y_hat, test_dataset: DataSet) -> None:
        self.logger.print("y_hat = {}".format([y_hat[i] for i in range(len(y_hat))]))
        self.logger.print("gt = {}".format([test_dataset[i] for i in range(len(test_dataset))]))
        return super().judge(y_hat, test_dataset)

if __name__ == '__main__':
    # 注册与运行
    WebManager().register_dataset(
        TestDataset(10), '10_nums'
    ).register_dataset(
        TestDataset(20), '20_nums'
    ).register_splitter(
        TestSplitter(0.8), 'ratio:0.8'
    ).register_splitter(
        TestSplitter(0.5), 'ratio:0.5'
    ).register_model(
        TestModel(1e-3)
    ).register_judger(
        TestJudger()
    ).start()
~~~