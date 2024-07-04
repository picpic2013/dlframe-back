from dlframe.cs_manager.Pkt import Pkt
from dlframe.cs_manager.consts import SERVER_ADDR_SPLITTER

class ModuleSender:
    def __init__(self, cs_manager, fn_addr, on_recv_fn) -> None:
        self.cs_manager = cs_manager
        self.fn_addr = fn_addr
        self.on_recv_fn = on_recv_fn

    def send(self, data: Pkt, to_addr):
        self.cs_manager.send(Pkt(
            f"{self.cs_manager.addr}{SERVER_ADDR_SPLITTER}{self.fn_addr}", 
            to_addr, data
        ))