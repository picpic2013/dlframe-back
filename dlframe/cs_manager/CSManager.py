import asyncio
import threading

from dlframe.cs_manager.Pkt import Pkt
from dlframe.cs_manager.Server import Server
from dlframe.cs_manager.Client import Client
from dlframe.cs_manager.ModuleSender import ModuleSender
from dlframe.cs_manager.utils import _is_local_addr, _is_control_packet
from dlframe.cs_manager.consts import SERVER_ADDR_SPLITTER, BROADCAST_PACKET_PREFIX, PING_PACKET_ADDR, PONG_PACKET_ADDR

class CSManager:
    def __init__(self, addr, host='0.0.0.0', port=8765, route_table=None) -> None:
        self.addr = addr
        self.host = host
        self.port = port
        self.event_loop = asyncio.new_event_loop()

        def on_connect_callback(websocket, path, send_queue):
            for fn in self.on_server_connect_callback_list:
                fn(websocket, path, send_queue)

        def on_recv_callback(websocket, pkt, path, send_queue):
            for fn in self.on_server_recv_callback_list:
                pkt = fn(websocket, pkt, path, send_queue)
                if pkt is None:
                    return
            self._forward(pkt)

        def on_disconnect_callback(websocket, path, send_queue):
            for fn in self.on_server_disconnect_callback_list:
                fn(websocket, path, send_queue)

        def on_send_callback(websocket, pkt, path, send_queue):
            for fn in self.on_server_send_callback_list:
                pkt = fn(websocket, pkt, path, send_queue)
                if pkt is None:
                    return

        def on_error_callback(websocket, pkt, e, msg):
            # print(f"Server Error: {msg}")
            for fn in self.on_server_error_callback_list:
                pkt = fn(websocket, pkt, e, msg)
                if pkt is None:
                    return

        self.server = Server(
            event_loop=self.event_loop, 
            self_addr=self.addr, 
            host=self.host, 
            port=self.port, 
            on_connect_callback=on_connect_callback, 
            on_recv_callback=on_recv_callback, 
            on_disconnect_callback=on_disconnect_callback, 
            on_send_callback=on_send_callback, 
            on_error_callback=on_error_callback
        )

        self.clients = dict() # {addr: Client}
        self.registered_fns = dict() 

        self.on_server_connect_callback_list = []
        self.on_server_recv_callback_list = []
        self.on_server_disconnect_callback_list = []
        self.on_server_send_callback_list = []
        self.on_server_error_callback_list = []

        self.on_client_connect_callback_list = []
        self.on_client_recv_callback_list = []
        self.on_client_disconnect_callback_list = []
        self.on_client_send_callback_list = []
        self.on_client_error_callback_list = []

        self.on_forward_callback_list = []
        self.on_forward_error_callback_list = []

        self.running_thread = threading.Thread(target=self._thread_worker)
        self.running_thread.daemon = True

        if route_table is None:
            route_table = dict()
        self.route_table = route_table
    def _forward(self, pkt: Pkt, to_server_addr=None):
        for fn in self.on_forward_callback_list:
            pkt = fn(pkt)
            if pkt is None:
                return
        to_addr = pkt.to_addr
        to_addr_split = to_addr.split(SERVER_ADDR_SPLITTER)
        if to_server_addr is None:
            to_server_addr = to_addr_split[0]
        to_fn_addr = to_addr_split[-1]
        if _is_local_addr(to_server_addr, self.addr):
            if to_fn_addr in self.registered_fns.keys():
                self.registered_fns[to_fn_addr].on_recv_fn(pkt.data, pkt.from_addr)
            elif not _is_control_packet(pkt):
                for fn in self.on_forward_error_callback_list:
                    pkt = fn(pkt, f"No fn route for pkt: {pkt}")
                    if pkt is None:
                        return
                # print(f"No fn route for pkt: {pkt}")
            return
        pkt.ttl -= 1
        if pkt.ttl <= 0:
            for fn in self.on_forward_error_callback_list:
                pkt = fn(pkt, f"TTL exceeded: {pkt}")
                if pkt is None:
                    return
            # print(f"TTL exceeded: {pkt}")
            return
        if self.server.has_link(to_server_addr):
            self.server.send(pkt)
        elif to_server_addr in self.clients.keys():
            self.clients[to_server_addr].send(pkt)
        elif to_server_addr in self.route_table.keys():
            pkt.ttl += 1
            self._forward(pkt, self.route_table[to_server_addr])
        else:
            for fn in self.on_forward_error_callback_list:
                pkt = fn(pkt, f"No route for pkt: {pkt}")
                if pkt is None:
                    return
            # print(f"No route for pkt: {pkt}")

    def _thread_worker(self):
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()

    def register_fn(self, fn_addr, on_recv_fn=None) -> ModuleSender:
        if on_recv_fn is None:
            on_recv_fn = lambda *x, **y: None
        module_sender = ModuleSender(self, fn_addr, on_recv_fn)
        self.registered_fns.setdefault(fn_addr, module_sender)
        return module_sender
    
    def register_event_callback(self, position, callback_fn):
        '''
        'on_server_connect': (websocket, path, send_queue) => None, <br>
        'on_server_disconnect': (websocket, path, send_queue) => None, <br>
        'on_server_recv': (websocket, pkt, path, send_queue) => Pkt, <br>
        'on_server_send': (websocket, pkt, path, send_queue) => Pkt, <br>
        'on_server_error': (websocket, pkt, exception, detail_txt, path, send_queue) => Pkt, <br>
        <br>
        'on_client_connect': (websocket) => None, <br>
        'on_client_disconnect': (websocket) => None, <br>
        'on_client_recv': (websocket, pkt) => Pkt, <br>
        'on_client_send': (websocket, pkt) => Pkt, <br>
        'on_client_error': (websocket, pkt, exception, detail_txt) => Pkt, <br>
        <br>
        'on_forward': (pkt) => Pkt, <br>
        'on_forward_error': (pkt, detail_txt) => Pkt, <br>
        '''
        if position == 'on_server_connect':
            self.on_server_connect_callback_list.append(callback_fn)
        elif position == 'on_server_recv':
            self.on_server_recv_callback_list.append(callback_fn)
        elif position == 'on_server_disconnect':
            self.on_server_disconnect_callback_list.append(callback_fn)
        elif position == 'on_server_send':
            self.on_server_send_callback_list.append(callback_fn)
        elif position == 'on_server_error':
            self.on_server_error_callback_list.append(callback_fn)
        elif position == 'on_client_connect':
            self.on_client_connect_callback_list.append(callback_fn)
        elif position == 'on_client_recv':
            self.on_client_recv_callback_list.append(callback_fn)
        elif position == 'on_client_disconnect':
            self.on_client_disconnect_callback_list.append(callback_fn)
        elif position == 'on_client_send':
            self.on_client_send_callback_list.append(callback_fn)
        elif position == 'on_client_error':
            self.on_client_error_callback_list.append(callback_fn)
        elif position == 'on_forward':
            self.on_forward_callback_list.append(callback_fn)
        elif position == 'on_forward_error':
            self.on_forward_error_callback_list.append(callback_fn)
        else:
            raise Exception(f"Invalid position: {position}")

    def connect(self, host, port=8765):
        client = Client(
            event_loop=self.event_loop, 
            self_addr=self.addr, 
            host=host, 
            port=port, 
            on_connect_callback=None, 
            on_recv_callback=None, 
            on_disconnect_callback=None, 
            on_send_callback=None, 
            on_error_callback=None
        )

        self.clients.setdefault(id(client), client)

        def on_connect_callback(websocket):
            client.send(Pkt(
                from_addr=self.addr, 
                to_addr=f"{BROADCAST_PACKET_PREFIX}{SERVER_ADDR_SPLITTER}{PING_PACKET_ADDR}", 
                data=PING_PACKET_ADDR.encode('utf-8')
            ))
            for fn in self.on_client_connect_callback_list:
                fn(websocket)

        def on_recv_callback(websocket, pkt):
            if _is_control_packet(pkt):
                to_server_addr = pkt.to_addr.split(SERVER_ADDR_SPLITTER)[0]
                to_fn_addr = pkt.to_addr.split(SERVER_ADDR_SPLITTER)[-1]
                from_addr = pkt.from_addr.split(SERVER_ADDR_SPLITTER)[0]
                if to_fn_addr == PING_PACKET_ADDR or to_fn_addr == PONG_PACKET_ADDR:
                    self.clients[from_addr] = client
                    self.clients.pop(id(client))
                if _is_local_addr(to_server_addr, self.addr) and to_fn_addr == PING_PACKET_ADDR:
                    self.links[from_addr].send(Pkt(
                        self.addr, 
                        f"{from_addr}{SERVER_ADDR_SPLITTER}{PONG_PACKET_ADDR}", 
                        PONG_PACKET_ADDR.encode('utf-8')
                    ))
            for fn in self.on_client_recv_callback_list:
                pkt = fn(websocket, pkt)
                if pkt is None:
                    return
            self._forward(pkt)

        def on_disconnect_callback(websocket):
            for fn in self.on_client_disconnect_callback_list:
                fn(websocket)

        def on_send_callback(websocket, pkt):
            for fn in self.on_client_send_callback_list:
                pkt = fn(websocket, pkt)
                if pkt is None:
                    return

        def on_error_callback(websocket, pkt, e, msg):
            # print(f"Client Error: {msg}")
            for fn in self.on_client_error_callback_list:
                pkt = fn(websocket, pkt, e, msg)
                if pkt is None:
                    return

        client.on_connect_callback = on_connect_callback
        client.on_recv_callback = on_recv_callback
        client.on_disconnect_callback = on_disconnect_callback
        client.on_send_callback = on_send_callback
        client.on_error_callback = on_error_callback

    def send(self, pkt):
        self._forward(pkt)

    def start(self):
        self.running_thread.start()