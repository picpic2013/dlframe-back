from dlframe.cs_manager.consts import BROADCAST_PACKET_PREFIX, SERVER_ADDR_SPLITTER, CONTROL_PACKET_PREFIX
from dlframe.cs_manager.Pkt import Pkt

def _is_local_addr(addr, self_addr):
    return addr == self_addr or addr.startswith(BROADCAST_PACKET_PREFIX)

def _setup_default(value, default):
    if value is None:
        return default
    return value

def _is_control_packet(packet: Pkt):
    to_fn_addr = packet.to_addr.split(SERVER_ADDR_SPLITTER)[-1]
    if to_fn_addr[:len(CONTROL_PACKET_PREFIX)] == CONTROL_PACKET_PREFIX:
        return True
    return False