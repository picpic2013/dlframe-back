# Dynamic Links

## 安装方法

~~~bash
pip install dynamic-links
~~~

## 简介

### 概述

Dynamic Links 是一个 python 元素管理框架，可以方便地构建 benchmark 等应用。

使用 Dynamic Links，用户仅需先定义应用中所需的元素、再定义执行逻辑，最后定义每个元素有哪些具体的 python 对象可选，即可通过 Web 页面配置并执行应用。

### 例子

~~~python
from dlframe import WebManager

def f1(x):
    print('f1', x)

def f2(x):
    print('f2', x)

# 定义元素管理器
with WebManager() as manager:
    func = manager.register_element('func', {
        'f1': f1, 
        'f2': f2
    })

    func('test')
~~~

运行程序，即可通过[前端](https://picpic2013.github.io/dlframe-front/)选择执行 `f1` 或 `f2`。

### 更复杂的例子

Dynamic Links 可以很方便地构建 benchmark 等应用。例如，如果要实现一个机器学习算法的简易框架，评估不同模型在不同参数下的各种指标，可以编写如下程序：

~~~python
from dlframe import WebManager

# 定义元素管理器
with WebManager() as manager:

    # 定义元素 + 定义元素可选的 python 对象
    dataset = manager.register_element('数据集', {
        'iris': IrisDataset(), 
        'watermelon': WatermelonDataset()
    })
    split_ratio = manager.register_element('数据分割比例', {
        '10%': 0.1, '30%': 0.3
    })
    Splitter = manager.register_element('数据分割器', {
        'k-fold': KFoldSplitter, 'random': RandomSplitter
    })
    learning_rate = manager.register_element('模型学习率', {
        'low': 1e-3, 'high': 1e-1
    })
    Model = manager.register_element('模型', {
        'cnn': CnnModel, 
        'resnet': ResnetModel
    })
    judger = manager.register_element('评价指标', {
        'accuracy': AccuracyJudger(), 'f1': F1ScoreJudger()
    })

    # 定义框架执行逻辑
    splitter = Splitter(split_ratio)
    train_data_test_data = splitter.split(dataset)
    train_data = train_data_test_data[0]
    test_data = train_data_test_data[1]
    
    model = Model(learning_rate)
    model.train(train_data)
    y_hat = model.test(test_data)

    judger.judge(y_hat, test_data)

~~~

此时运行程序，即可通过[前端](https://picpic2013.github.io/dlframe-front/)页面配置具体使用哪个 python 对象作为元素，并执行定义的逻辑代码。

### 对 python 语法的支持

注意！目前本框架在定义执行逻辑时，元素仅支持函数、类、对象、原生 python 对象等，且仅对 python 的基础语法提供支持。目前框架暂不支持元组等的自动解包操作。如需要解包，请使用 `index` 代替。例如：

~~~python
# 不支持！
train_data, test_data = splitter.split(dataset)

# 请用以下代码替换
train_data_test_data = splitter.split(dataset)
train_data = train_data_test_data[0]
test_data = train_data_test_data[1]
~~~

### 日志模块

框架提供了 logger，开发者可以方便地向前端输出文本 (print) 和图片 (imshow)。

~~~python
# import Logger
from dlframe import Logger

# 注册一个名为 Test Logger 的 Logger
logger = Logger.get_logger('Test Logger')

# logger 支持打印文字
logger.print('str1', 'str2', end='\t')

# logger 支持显示图片
logger.imshow(
    np.random.randint(
        0, 256, (100, 100, 3), 
        dtype=np。uint8
    )
)
~~~

### 并行模块

框架默认按照定义的框架执行逻辑顺序执行，您也可以通过`parallel=True`手动开启并行执行(TODO: 目前仅为单线程)。此时，本框架会按照定义逻辑的拓扑排序执行代码。对于拓扑排序结果相同的，不保证执行的先后顺序。例如：

~~~python
with WebManager(parallel=True) as manager:
    clsss = manager.register_element('cls_1', {
        'c1': A('c1'), 
        'c2': A('c2')
    })

    clsss.f1()
    clsss.f2()
    clsss.f3()
~~~

三个函数执行顺序可能不同。如果希望按 f1, f2, f3的顺序执行，可以使用 `>` 和 `<` 指定节点顺序。例如：

~~~python
clsss.f1() > clsss.f2() > clsss.f3()
~~~

也可指定元素运算顺序，比如：

~~~python
with WebManager(parallel=True) as manager:
    clsss = manager.register_element('cls_1', {
        'c1': A('c1'), 
        'c2': A('c2')
    })

    result1 = clsss.f1()
    result2 = clsss.f2()
~~~

如果需要指定 `result1` 优先于 `result2` 得到结果，则可以指定：

~~~python
result1 > result2
~~~

变量和方法可以混用。例如：

~~~python
result1 > clsss.f2()
~~~

--- 

### 前端

本框架仅提供 WebSocket 服务，不提供页面显示。需配合[前端](https://picpic2013.github.io/dlframe-front/)使用。前端代码开源在[仓库](https://github.com/picpic2013/dlframe-front.git)。

注意！由于底层使用 `ws`，对于某些浏览器，可能无法通过安全检查，从而导致前后端无法连接。请禁用相关安全策略后重试。