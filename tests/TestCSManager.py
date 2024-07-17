import time

from dlframe import CSManager

if __name__ == '__main__':
    manager1 = CSManager(addr="server1", host="0.0.0.0", port=8765)
    manager1.start()

    manager2 = CSManager(addr="server2", host="0.0.0.0", port=8767, route_table={'server3': 'server1'})
    manager2.connect('127.0.0.1', 8765)
    manager2.start()

    manager3 = CSManager(addr="server3", host="0.0.0.0", port=8769, route_table={'server2': 'server1'})
    manager3.connect('127.0.0.1', 8765)
    manager3.start()

    def on_forward(pkt):
        print(str(pkt))
        return pkt

    manager1.register_event_callback(
        "on_forward", 
        on_forward
    )

    def recv(data, from_addr):
        print(from_addr, ':',data.decode('utf-8'))
    
    manager3.register_fn("recv", recv)
    # manager2.register_fn("recv", recv)
    # manager1.register_fn("recv", recv)
    # sender = manager1.register_fn("send")
    sender = manager2.register_fn("send")

    time.sleep(0.5)
    for _ in range(10):
        
        sender.send(str(_).encode('utf-8'), "server3/recv")
        # sender.send(str(_).encode('utf-8'), "server1/recv")
        time.sleep(1)
        