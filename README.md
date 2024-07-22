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
    
    # 定义元素 + 定义元素可选的 python 对象
    func = manager.register('func', {
        'function1': f1, 
        'function2': f2
    })

    # 定义框架执行逻辑
    func('test')
~~~

运行程序，即可通过[前端](https://picpic2013.github.io/dlframe-front/)选择执行 `f1` 或 `f2`。

### 另一个例子

~~~python
from dlframe import WebManager

manager = WebManager()

# 定义元素可选的 python 对象
@manager.register('func', 'function1')
# 也可 @manager.register('func') 会自动以 f1 作为选项名称
def f1(x):
    print('f1', x)

# 定义元素可选的 python 对象
@manager.register('func', 'function2')
def f2(x):
    print('f2', x)

# 定义元素管理器
with manager:
    
    # 定义元素
    func = manager['func']

    # 定义框架执行逻辑
    func('test')
~~~

与上一个例子完全等价。

### 又一个例子
~~~python
from dlframe import WebManager

def f1(x):
    print('f1', x)

def f2(x):
    print('f2', x)

# 定义元素管理器
with WebManager() as manager:
    # 定义元素可选的 python 对象
    manager.register('func', 'function1', f1)
    manager.register('func', 'function2', f2)

    # 定义元素
    func = manager['func']

    # 定义框架执行逻辑
    func('test')
~~~

与上一个例子完全等价。

### 更复杂的例子

Dynamic Links 可以很方便地构建 benchmark 等应用。例如，如果要实现一个机器学习算法的简易框架，评估不同模型在不同参数下的各种指标，可以编写如下程序：

~~~python
from dlframe import WebManager

# 定义元素管理器
with WebManager() as manager:

    # 定义元素 + 定义元素可选的 python 对象
    dataset = manager.register('数据集', {
        'iris': IrisDataset(), 
        'watermelon': WatermelonDataset()
    })
    split_ratio = manager.register('数据分割比例', {
        '10%': 0.1, '30%': 0.3
    })
    Splitter = manager.register('数据分割器', {
        'k-fold': KFoldSplitter, 'random': RandomSplitter
    })
    Model = manager.register('模型', {
        'decision-tree': DecisionTreeModel, 
        'svm': SVMModel
    })
    judger = manager.register('评价指标', {
        'accuracy': AccuracyJudger(), 'f1': F1ScoreJudger()
    })

    # 定义框架执行逻辑
    splitter = Splitter(split_ratio)
    train_data_test_data = splitter.split(dataset)
    train_data = train_data_test_data[0]
    test_data = train_data_test_data[1]
    
    model = Model()
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
        dtype=np.uint8
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

### 指定运行 ip 与端口号

~~~python
with WebManager(host='0.0.0.0', port=8765):
    pass
~~~

## 互联模块

本项目提供一个互联模块，可以方便的在各个 python 函数之间传递数据。该模块使用 `websocket` 实现，其拥有一个服务端和多个客户端模块。使用时可先创建 Manager 对象，绑定服务端地址前缀和 tcp 地址与端口，设定路由表，并调用 `manager.start()` 启动 manager 的事件循环。期间可以使用 `manager.connect(host, port)` 函数连接其他 manager。

~~~ python

from dlframe import CSManager

manager1 = CSManager(
    addr="server1", 
    host="0.0.0.0", 
    port=8765
)
manager1.start()

manager2 = CSManager(
    addr="server2", 
    host="0.0.0.0", 
    port=8767, 
    route_table={'server3': 'server1'}
)
manager2.connect('127.0.0.1', 8765)
manager2.start()

manager3 = CSManager(
    addr="server3", 
    host="0.0.0.0", 
    port=8769, 
    route_table={'server2': 'server1'}
)
manager3.connect('127.0.0.1', 8765)
manager3.start()

~~~

然后可以为每个函数注册一个专属地址，即可收发消息。`send` 发出的消息会被转发到目标地址的 `recv` 函数。

~~~ python

def recv(data, from_addr):
    print(from_addr, ':',data.decode('utf-8'))

manager3.register_fn("recv", recv)
sender = manager2.register_fn("send")

time.sleep(0.5)

sender.send('hello'.encode('utf-8'), "server3/recv")

~~~

本模块支持一些钩子函数，开发者可以自由注册事件回调函数，互联模块将在特定事件发生时，调用注册的回调函数。例如：

~~~ python

def on_forward(pkt):
    print(str(pkt))
    return pkt

manager1.register_event_callback(
    "on_forward", on_forward
)

~~~

此外，本模块还支持其它回调函数：

~~~ javascript

{
    'on_server_connect': (websocket, path, send_queue) => None, 
    'on_server_disconnect': (websocket, path, send_queue) => None, 
    'on_server_recv': (websocket, pkt, path, send_queue) => Pkt, 
    'on_server_send': (websocket, pkt, path, send_queue) => Pkt, 
    'on_server_error': (websocket, pkt, exception, detail_txt, path, send_queue) => Pkt, 

    'on_client_connect': (websocket) => None, 
    'on_client_disconnect': (websocket) => None, 
    'on_client_recv': (websocket, pkt) => Pkt, 
    'on_client_send': (websocket, pkt) => Pkt, 
    'on_client_error': (websocket, pkt, exception, detail_txt) => Pkt, 

    'on_forward': (pkt) => Pkt, 
    'on_forward_error': (pkt, detail_txt) => Pkt, 
}

~~~

## 关于前端

本框架仅提供 WebSocket 服务，不提供页面显示。需配合[前端](https://picpic2013.github.io/dlframe-front/)使用。前端代码开源在[仓库](https://github.com/picpic2013/dlframe-front.git)。

注意！由于底层使用 `ws`，对于某些浏览器，可能无法通过安全检查，从而导致前后端无法连接。请禁用相关安全策略后重试。

## 其它工具

### PIC_Timer
~~~ python
# example 1
# function timer
print('='*50, 'example 1', '='*50)
@PICTimer
def f1():
    for _ in range(100000):
        b = _

f1()

# example 2
# with code block
print('='*50, 'example 2', '='*50)
with PICTimer.getTimer('example2') as t:
    for _ in range(1, 100000):
        if _ % 20000 == 0:
            t.showTime()
        bb = _

# example 3
print('='*50, 'example 3', '='*50)

timer = PICTimer.getTimer('example3') 
timer.startTimer()                    
# or `timer = PICTimer.getTimer('example3', autoStart=True)`

for idx in range(3):
    for _ in range(1, 100000):
        if _ % 20000 == 0:
            timer.showTime("stage_" + str(_))
        bb = _
    timer.forceShowTime() # you can output results before summary
timer.summary()

# example 4
# create sub-timer
print('='*50, 'example 4', '='*50)
timer = PICTimer.getTimer('example4', autoStart=True)
for idx in range(3):
    subTimer = timer.getTimer('sub_' + str(idx), autoStart=True)
    for _ in range(1, 100000):
        if _ % 20000 == 0:
            subTimer.showTime("stage_" + str(_))
        bb = _
    timer.showTime()
timer.summary()
~~~

### make_recursive_func
~~~ python
# dict args
arg1 = {idx: 'arg1_k_'+str(idx) for idx in range(3)}
arg2 = {idx: 'arg2_k_'+str(idx) for idx in range(3)}

# list args
arg1 = [_ for _ in range(10)]
arg2 = [_ for _ in range(10)]

# tuple / generator args
arg1 = (_ for _ in range(10))
arg2 = (_ for _ in range(10))

# non-iterable args
arg1 = 0
arg2 = 1

# mutiple args
arg1 = {idx: ['arg1_k_'+str(idx)+'_l_'+str(_) for _ in range(2)] for idx in range(3)}
arg2 = {idx: ['arg2_k_'+str(idx)+'_l_'+str(_) for _ in range(2)] for idx in range(3)}

@make_recursive_func
def f1(x, base):
    return base.format(x)

@make_recursive_func
def f2(x, y, base):
    return base.format(x, y)

@make_recursive_func
def f3(x, y, base1, base2):
    return base1.format(x), base2.format(y)

@make_multi_return_recursive_func
def f4(x, y, base1, base2):
    return base1.format(x), base2.format(y)

res1 = f1(arg1, base="arg1: {}")
res2 = f2(arg1, arg2, base="arg1: {}, arg2: {}")
res3 = f3(arg1, arg2, base1="arg1: {}", base2=" arg2: {}")
res4 = f4(arg1, arg2, base1="arg1: {}", base2=" arg2: {}")

print(res1)
print(res2)
print(res3)
print(res4)
~~~