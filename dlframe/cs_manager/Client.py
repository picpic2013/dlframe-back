import asyncio
import websockets

from dlframe.cs_manager.Pkt import Pkt
from dlframe.cs_manager.utils import _setup_default

class Client:
    def __init__(self, event_loop, self_addr, host, port=8765, on_connect_callback=None, on_recv_callback=None, on_disconnect_callback=None, on_send_callback=None, on_error_callback=None) -> None:
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

        self.send_queue = asyncio.Queue()
        self._setup_send_recv_async()

    def _setup_send_recv_async(self):
        async def consumer_handler(websocket):
            self.on_connect_callback(websocket)
            async for message in websocket:
                try:
                    message = Pkt.from_binary(message)
                except Exception as e:
                    # print(f"Error parsing pkt: {e}")
                    self.on_error_callback(websocket, message, e, f"Error parsing pkt: {e}")
                    continue
                self.on_recv_callback(websocket, message)
                # print(f"Received message: {message}")
            self.on_disconnect_callback(websocket)

        async def producer_handler(websocket):
            while True:
                message = await self.send_queue.get()
                self.on_send_callback(websocket, message)
                await websocket.send(message.to_binary())
                # print(f"Sent message: {message}")
        async def handler():
            uri = f"ws://{self.host}:{self.port}"
            async with websockets.connect(uri) as websocket:
                consumer_task = asyncio.ensure_future(consumer_handler(websocket), loop=self.event_loop)
                producer_task = asyncio.ensure_future(producer_handler(websocket), loop=self.event_loop)

                done, pending = await asyncio.wait(
                    [consumer_task, producer_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in pending:
                    task.cancel()
        
        self.event_loop.create_task(handler())

    def send(self, packet: Pkt):
        asyncio.run_coroutine_threadsafe(
            self.send_queue.put(packet), 
            self.event_loop
        )