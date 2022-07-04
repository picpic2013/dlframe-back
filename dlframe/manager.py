from __future__ import annotations
from email.policy import default

from typing import Dict, List, Tuple

from dlframe.dataset import DataSet
from dlframe.splitter import Splitter
from dlframe.model import Model
from dlframe.judger import Judger
from dlframe.logger import CmdLogger

class ManagerConfig:

    dataset: str
    splitter: str
    model: str
    judger: str

    dataset_params: Dict[str, str]
    splitter_params: Dict[str, str]
    model_params: Dict[str, str]
    judger_params: Dict[str, str]

    def __init__(self, dataset, splitter, model, judger, dataset_params=None, splitter_params=None, model_params=None, judger_params=None) -> None:
        self.dataset = dataset
        self.splitter = splitter
        self.model = model
        self.judger = judger

        self.dataset_params = {} if dataset_params is None else dataset_params
        self.splitter_params = {} if splitter_params is None else splitter_params
        self.model_params = {} if model_params is None else model_params
        self.judger_params = {} if judger_params is None else judger_params


class Manager:
    datasets: Dict[str, DataSet]
    splitters: Dict[str, Splitter]
    models: Dict[str, Model]
    judgers: Dict[str, Judger]

    def __init__(self) -> None:
        self.datasets = {}
        self.splitters = {}
        self.models = {}
        self.judgers = {}

    def register_dataset(self, dataset: DataSet, name: str=None) -> Manager:
        if name is None:
            name = dataset.__class__.__name__
        assert name not in self.datasets.keys(), 'name already exists'
        self.datasets.setdefault(name, dataset)
        return self

    def register_splitter(self, splitter: Splitter, name: str=None) -> Manager:
        if name is None:
            name = splitter.__class__.__name__
        assert name not in self.splitters.keys(), 'name already exists'
        self.splitters.setdefault(name, splitter)
        return self

    def register_model(self, model: Model, name: str=None) -> Manager:
        if name is None:
            name = model.__class__.__name__
        assert name not in self.models.keys(), 'name already exists'
        self.models.setdefault(name, model)
        return self

    def register_judger(self, judger: Judger, name: str=None) -> Manager:
        if name is None:
            name = judger.__class__.__name__
        assert name not in self.judgers.keys(), 'name already exists'
        self.judgers.setdefault(name, judger)
        return self

    def inspect(self, name: str) -> Tuple[List[str], List[str]]:
        '''
        name -> [paramName, defaultValues]
        '''
        obj = None
        if name in self.datasets.keys():
            obj = self.datasets[name]
        elif name in self.splitters.keys():
            obj = self.splitters[name]
        elif name in self.models.keys():
            obj = self.models[name]
        elif name in self.judgers.keys():
            obj = self.judgers[name]        
        else:
            raise 'unknown name'

        names = []
        defaults = []
        for key, value in vars(obj).items():
            if key == 'logger':
                continue
            names.append(key)
            defaults.append(value)
        return names, defaults

    def run(self, conf: ManagerConfig) -> None:
        assert conf.dataset in self.datasets.keys(), 'unknown dataset class name'
        dataset = self.datasets[conf.dataset]
        for key, value in conf.dataset_params.items():
            setattr(dataset, key, value)

        assert conf.splitter in self.splitters.keys(), 'unknown splitter class name'
        splitter = self.splitters[conf.splitter]
        for key, value in conf.splitter_params.items():
            setattr(splitter, key, value)

        assert conf.model in self.models.keys(), 'unknown model class name'
        model = self.models[conf.model]
        for key, value in conf.model_params.items():
            setattr(model, key, value)

        assert conf.judger in self.judgers.keys(), 'unknown judger class name'
        judger = self.judgers[conf.judger]
        for key, value in conf.judger_params.items():
            setattr(judger, key, value)

        train_data, test_data = splitter.split(dataset)
        model.train(train_data)
        y_hat = model.test(test_data)
        judger.judge(y_hat, test_data)

class CmdManager(Manager):
    def __init__(self) -> None:
        super().__init__()

    def register_dataset(self, dataset: DataSet, name: str = None) -> Manager:
        if name is None:
            name = dataset.__class__.__name__
        dataset.logger = CmdLogger(name)
        return super().register_dataset(dataset, name)

    def register_judger(self, judger: Judger, name: str = None) -> Manager:
        if name is None:
            name = judger.__class__.__name__
        judger.logger = CmdLogger(name)
        return super().register_judger(judger, name)

    def register_model(self, model: Model, name: str = None) -> Manager:
        if name is None:
            name = model.__class__.__name__
        model.logger = CmdLogger(name)
        return super().register_model(model, name)

    def register_splitter(self, splitter: Splitter, name: str = None) -> Manager:
        if name is None:
            name = splitter.__class__.__name__
        splitter.logger = CmdLogger(name)
        return super().register_splitter(splitter, name)

    def start(self):

        def inputUntilCorrect(instruction, minn, maxx):
            while True:
                try:
                    choice = int(input(instruction))
                    if choice >= minn and choice < maxx:
                        return choice
                    print('invalid index')
                except:
                    print('please input index number')
        
        def inputParams(dataset_params, dataset_defaults):
            paramDict = {}
            if dataset_params is None:
                dataset_params = []
            if dataset_defaults is None:
                dataset_defaults = []
            deltaLength = len(dataset_params) - len(dataset_defaults)
            for paramIdx in range(len(dataset_params)):
                name = dataset_params[paramIdx]
                if name == 'self' and paramIdx == 0:
                    continue
                if paramIdx >= deltaLength:
                    default_value = dataset_defaults[paramIdx - deltaLength]
                    value = input('param [{}]: (default: {})'.format(name, default_value))
                    if value == '':
                        value = default_value
                else:
                    value = input('param [{}]: '.format(name))
                    if value == '':
                        continue
                paramDict.setdefault(name, value)
            return paramDict


        exit_program = False
        while not exit_program:
            assert len(self.datasets) != 0, 'no dataset'
            for idx, name in enumerate(self.datasets.keys()):
                print('{:3d}'.format(idx), name)
            choice = inputUntilCorrect('please choose dataset: ', 0, len(self.datasets))
            dataset_name = list(self.datasets.keys())[choice]
            dataset_params, dataset_defaults = self.inspect(dataset_name)
            dataset_params = inputParams(dataset_params, dataset_defaults)
            print('='*50)

            assert len(self.splitters) != 0, 'no splitter'
            for idx, name in enumerate(self.splitters.keys()):
                print('{:3d}'.format(idx), name)
            choice = inputUntilCorrect('please choose splitter: ', 0, len(self.splitters))
            splitter_name = list(self.splitters.keys())[choice]
            splitter_params, splitter_defaults = self.inspect(splitter_name)
            splitter_params = inputParams(splitter_params, splitter_defaults)
            print('='*50)

            assert len(self.models) != 0, 'no model'
            for idx, name in enumerate(self.models.keys()):
                print('{:3d}'.format(idx), name)
            choice = inputUntilCorrect('please choose model: ', 0, len(self.models))
            model_name = list(self.models.keys())[choice]
            model_params, model_defaults = self.inspect(model_name)
            model_params = inputParams(model_params, model_defaults)
            print('='*50)

            assert len(self.judgers) != 0, 'no judger'
            for idx, name in enumerate(self.judgers.keys()):
                print('{:3d}'.format(idx), name)
            choice = inputUntilCorrect('please choose judger: ', 0, len(self.judgers))
            judger_name = list(self.judgers.keys())[choice]
            judger_params, judger_defaults = self.inspect(judger_name)
            judger_params = inputParams(judger_params, judger_defaults)
            print('='*50)

            conf = ManagerConfig(
                dataset_name, splitter_name, model_name, judger_name, 
                dataset_params, splitter_params, model_params, judger_params
            )

            self.run(conf)

            exit_program = input('Done! input [q] to quit or [Enter] to continue') == 'q'