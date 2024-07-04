class LinkSender:
    def __init__(self, addr, websocket, path, send_queue) -> None:
        self.addr = addr
        self.websocket = websocket
        self.path = path
        self.send_queue = send_queue

    def send(self, message):
        self.send_queue.put_nowait(message)