import zmq
from threading import Thread
import pickle
context = zmq.Context()

# 远程过程调用的绑定端口
rpc_bind_address = "tcp://*:5558"

# RPC服务处理类
class RPCHandler:
    def __init__(self):
        self._functions = {}
        # 创建上下文对象
        t2 = Thread(target=self.rpc_server, args=())
        # t2.daemon = True
        t2.start()

    def register_function(self, func):
        self._functions[func.__name__] = func

    def handle_connection(self, data):
        # print(data)
        func_name, args, kwargs = pickle.loads(data)
        print(func_name, args, kwargs)
        result = self._functions[func_name](*args, **kwargs)
        return result



    def rpc_server(self):
        # socket不能定义在线程外！
        self.reply_socket = context.socket(zmq.REP)
        self.reply_socket.bind(rpc_bind_address)
        while True:
            data = self.reply_socket.recv()
            result = None
            try:
                result = self.handle_connection(data)
            except Exception as e:
                print(e)
            finally:
                self.reply_socket.send_json({"result": result})






