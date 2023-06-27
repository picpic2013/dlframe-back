# DL-Frame

一个及其简易的机器学习可视化框架，用户仅需实现：
- 定义模块
- 定义计算图
- 注册模块实例

--- 

框架提供了 logger，开发者可以方便地向前端输出文本 (print) 和图片 (imshow)。

--- 

参考运行逻辑：

~~~python
dataset = manager.register_element('数据集')
splitter = manager.register_element('数据分割')
model = manager.register_element('模型')
judger = manager.register_element('评价指标')

train_data_test_data = splitter.split(dataset)
train_data, test_data = train_data_test_data[0], train_data_test_data[1]
model.train(train_data)
y_hat = model.test(test_data)

# if you want model.conclusion execute after y_hat, you can do this
# you can also use model.conclusion() < y_hat
y_hat > model.conclusion()

judger.judge(y_hat, test_data)
~~~

--- 

本框架仅提供 WebSocket 服务，不提供页面显示。需配合[前端](https://picpic2013.github.io/dlframe-front/)使用。前端代码开源在[仓库](https://github.com/picpic2013/dlframe-front.git)。

## 安装方法

~~~bash
# 可选，新建 conda 环境
conda create -n dlframe python=3.10
conda activate dlframe

# 安装
pip install git+https://github.com/picpic2013/dlframe-back
~~~

## 测试用例

~~~bash
python tests/Display.py
~~~
