import asyncio
import websockets

from dlframe.cs_manager.Pkt import Pkt
from dlframe.cs_manager.LinkSender import LinkSender
from dlframe.cs_manager.utils import _setup_default, _is_control_packet, _is_local_addr
from dlframe.cs_manager.consts import SERVER_ADDR_SPLITTER, PING_PACKET_ADDR, PONG_PACKET_ADDR

class Server:
    def __init__(self, event_loop, self_addr, host='0.0.0.0', port=8765, on_connect_callback=None, on_recv_callback=None, on_disconnect_callback=None, on_send_callback=None, on_error_callback=None) -> None:
        self.self_addr = self_addr
        self.host = host
        self.port = port
        self.event_loop = event_loop

        _default_callback_fn = lambda *a, **kw: None

        self.on_connect_callback = _setup_default(on_connect_callback, _default_callback_fn)
        self.on_recv_callback = _setup_default(on_recv_callback, _default_callback_fn)
        self.on_disconnect_callback = _setup_default(on_disconnect_callback, _default_callback_fn)
        self.on_send_callback = _setup_default(on_send_callback, _default_callback_fn)
        self.on_error_callback = _setup_default(on_error_callback, _default_callback_fn)

        self.links = dict() # {addr: LinkSender}
        self._setup_send_recv_async()

    def _setup_send_recv_async(self):
        async def consumer_handler(websocket, path, send_queue):
            self.on_connect_callback(websocket, path, send_queue)
            async for message in websocket:
                try:
                    message = Pkt.from_binary(message)
                except Exception as e:
                    # print(f"Error parsing pkt: {e}")
                    self.on_error_callback(websocket, message, e, f"Error parsing pkt: {e}", path, send_queue)
                    continue
                # must judge control packet then call on_recv_callback
                if _is_control_packet(message):
                    self._handle_control_packet(websocket, message, path, send_queue)
                self.on_recv_callback(websocket, message, path, send_queue)
                # print(f"Received message: {message}")
            self.on_disconnect_callback(websocket, path, send_queue)

        async def producer_handler(websocket, path, send_queue):
            while True:
                message = await send_queue.get()
                self.on_send_callback(websocket, message, path, send_queue)
                await websocket.send(message.to_binary())
                # print(f"Sent message: {message}")

        async def handler(websocket, path):
            send_queue = asyncio.Queue()

            consumer_task = asyncio.ensure_future(consumer_handler(websocket, path, send_queue), loop=self.event_loop)
            producer_task = asyncio.ensure_future(producer_handler(websocket, path, send_queue), loop=self.event_loop)
            done, pending = await asyncio.wait(
                [consumer_task, producer_task], 
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

        start_server = websockets.serve(handler, self.host, self.port, loop=self.event_loop)
        self.event_loop.run_until_complete(start_server)
    
    def _handle_control_packet(self, websocket, message, path, send_queue):
        to_server_addr = message.to_addr.split(SERVER_ADDR_SPLITTER)[0]
        to_fn_addr = message.to_addr.split(SERVER_ADDR_SPLITTER)[-1]
        from_addr = message.from_addr.split(SERVER_ADDR_SPLITTER)[0]
        if to_fn_addr == PING_PACKET_ADDR or to_fn_addr == PONG_PACKET_ADDR:
            self.links[from_addr] = LinkSender(
                from_addr, 
                websocket, 
                path, 
                send_queue, 
                self.event_loop
            )
        if _is_local_addr(to_server_addr, self.self_addr) and to_fn_addr == PING_PACKET_ADDR:
            self.links[from_addr].send(Pkt(
                self.self_addr, 
                f"{from_addr}{SERVER_ADDR_SPLITTER}{PONG_PACKET_ADDR}", 
                PONG_PACKET_ADDR.encode('utf-8')
            ))
    
    def has_link(self, addr):
        return addr in self.links.keys()

    def send(self, packet: Pkt):
        to_addr = packet.to_addr.split(SERVER_ADDR_SPLITTER)[0]
        if self.has_link(to_addr):
            asyncio.run_coroutine_threadsafe(
                self.links[to_addr].send_queue.put(packet), 
                self.event_loop
            )
            
        else:
            self.on_error_callback(None, None, None, f"No route to {to_addr}", None, None)