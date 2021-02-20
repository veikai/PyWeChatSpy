import zmq
import pickle

context = zmq.Context()
# 服务端远程过程调用的ip和端口
rpc_server_address = "tcp://127.0.0.1:5558"

# RPC服务代理类
class RPCProxy:
    def __getattr__(self, name):
        def do_rpc(*args, **kwargs):
            tmp_socket = context.socket(zmq.REQ)
            tmp_socket.connect(rpc_server_address)
            tmp_socket.send(pickle.dumps((name, args, kwargs)))
            result = tmp_socket.recv_json()
            return result
        return do_rpc


