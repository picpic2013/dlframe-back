from __future__ import annotations

from typing import Dict, List, Tuple

from dataset import DataSet
from splitter import Splitter
from model import Model
from judger import Judger

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
        if name in self.datasets.keys():
            obj = self.datasets[name]
            names = obj.__init__.__code__.co_varnames
            defaults = obj.__init__.__defaults__
            return names, defaults

        elif name in self.splitters.keys():
            obj = self.splitters[name]
            names = obj.__init__.__code__.co_varnames
            defaults = obj.__init__.__defaults__
            return names, defaults

        elif name in self.models.keys():
            obj = self.models[name]
            names = obj.__init__.__code__.co_varnames
            defaults = obj.__init__.__defaults__
            return names, defaults

        elif name in self.judgers.keys():
            obj = self.judgers[name]
            names = obj.__init__.__code__.co_varnames
            defaults = obj.__init__.__defaults__
            return names, defaults
        
        else:
            raise 'unknown name'

    def run(self, conf: ManagerConfig) -> None:
        assert conf.dataset in self.datasets.keys(), 'unknown dataset class name'
        dataset = self.datasets[conf.dataset]
        for key, value in conf.dataset_params.items():
            setattr(dataset, key, value)

        assert conf.splitter in self.splitters.keys(), 'unknown splitter class name'
        splitter = self.splitters[conf.splitter]
        for key, value in conf.splitter.items():
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