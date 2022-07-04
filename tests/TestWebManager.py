import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(
        os.path.abspath(__file__), '..', '..'
    )
))

from dlframe import WebManager, DirectSplitter
from TestCmdManager import DebugDataset, DebugModel, DebugJudger

if __name__ == '__main__':
    WebManager().register_dataset(
        DebugDataset(10), '10_ints'
    ).register_dataset(
        DebugDataset(20), '20_ints'
    ).register_splitter(
        DirectSplitter(0.8), 'split-8:2'
    ).register_splitter(
        DirectSplitter(0.5), 'split-5:5'
    ).register_model(
        DebugModel()
    ).register_judger(
        DebugJudger()
    ).start()