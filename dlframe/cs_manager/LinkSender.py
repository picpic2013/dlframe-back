import asyncio

class LinkSender:
    def __init__(self, addr, websocket, path, send_queue, event_loop) -> None:
        self.addr = addr
        self.websocket = websocket
        self.path = path
        self.send_queue = send_queue
        self.event_loop = event_loop

    def send(self, pkt):
        asyncio.run_coroutine_threadsafe(
            self.send_queue.put(pkt), 
            self.event_loop
        )