from dlframe.logger import Logger
from dlframe.manager import Manager, ManagerConfig

import asyncio
import websockets
import json
import queue
import threading
import traceback

class WebLogger(Logger):
    def __init__(self, socket, name='untitled') -> None:
        super().__init__()
        self.socket = socket
        self.name = name

    def print(self, *params, end='\n') -> Logger:
        self.socket.send(json.dumps({
            'status': 200, 
            'type': 'print', 
            'data': {
                'content': '[{}]: '.format(self.name) + ' '.join([str(_) for _ in params]) + end
            }
        }))
        return super().print(*params, end=end)

    def progess(self, percentage: float) -> Logger:
        return super().progess(percentage)

class SendSocket:
    def __init__(self, socket) -> None:
        self.sendBuffer = queue.Queue()
        self.socket = socket
        self.sendThread = threading.Thread(target=self.threadWorker, daemon=True)
        self.sendThread.start()

    def threadWorker(self):
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        event_loop.run_until_complete(self.sendWorker())

    async def sendWorker(self):
        while True:
            content = self.sendBuffer.get()
            await self.socket.send(content)

    def send(self, content: str):
        self.sendBuffer.put(content)

class WebManager(Manager):
    def __init__(self) -> None:
        super().__init__()

    def start(self, host='0.0.0.0', port=8765) -> None:
        event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(event_loop)
        async def onRecv(socket, path):
            msgIdx = -1
            sendSocket = SendSocket(socket)
            async for message in socket:
                msgIdx += 1
                message = json.loads(message)
                # print(msgIdx, message)

                # key error
                if not all([key in message.keys() for key in ['type', 'params']]):
                    response = json.dumps({
                        'status': 500, 
                        'data': 'no key param'
                    })
                    await socket.send(response)
                
                # key correct
                else:
                    if message['type'] == 'overview':
                        response = json.dumps({
                            'status': 200, 
                            'type': 'overview', 
                            'data': {
                                'datasets': list(self.datasets.keys()), 
                                'splitters': list(self.splitters.keys()), 
                                'models': list(self.models.keys()), 
                                'judgers': list(self.judgers.keys())
                            }
                        })
                        await socket.send(response)

                    elif message['type'] == 'run':
                        params = message['params']
                        conf = ManagerConfig(
                            params['datasetName'], 
                            params['splitterName'], 
                            params['modelName'], 
                            params['judgerName'], 

                            dataset_params={'logger': WebLogger(sendSocket, params['datasetName'])}, 
                            splitter_params={'logger': WebLogger(sendSocket, params['splitterName'])}, 
                            model_params={'logger': WebLogger(sendSocket, params['modelName'])}, 
                            judger_params={'logger': WebLogger(sendSocket, params['judgerName'])}, 
                        )

                        try:
                            self.run(conf)
                        except Exception as e:
                            response = json.dumps({
                                'status': 200, 
                                'type': 'print', 
                                'data': {
                                    'content': traceback.format_exc()
                                }
                            })
                            await socket.send(response)
                    
                    # unknown key
                    else:
                        response = json.dumps({
                            'status': 500, 
                            'data': 'unknown type'
                        })
                        await socket.send(response)

        print('server is running at [{}:{}]...'.format(host, port))
        event_loop.run_until_complete(websockets.serve(onRecv, host, port))
        event_loop.run_forever()