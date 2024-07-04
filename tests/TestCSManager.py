import time

from dlframe import CSManager

if __name__ == '__main__':
    manager1 = CSManager(addr="server1", host="0.0.0.0", port=8765)
    manager1.start()

    manager2 = CSManager(addr="server2", host="0.0.0.0", port=8767)
    manager2.start()

    manager2.connect('127.0.0.1', 8765)

    def recv(data):
        print(data, data.decode('utf-8'))
    
    manager2.register_fn("recv", recv)
    # manager1.register_fn("recv", recv)
    sender = manager1.register_fn("send")
    # sender = manager2.register_fn("send")

    time.sleep(1)
    for _ in range(10):
        
        sender.send(str(_).encode('utf-8'), "server2/recv")
    
    time.sleep(100)
        