from PyWeChatSpy import WeChatSpy
import logging
from rpc_server_tools import *
from queue import Queue
import zmq
import time
from google.protobuf.descriptor import FieldDescriptor as FD

my_response_queue = Queue()
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.INFO)
logger.addHandler(sh)

contact_list = []
chatroom_list = []

# pb格式转dict
def pb2dict(obj):
    """
    Takes a ProtoBuf Message obj and convertes it to a dict.
    """
    try:
        adict = {}
        if not obj.IsInitialized():
            return None
        for field in obj.DESCRIPTOR.fields:
            if not getattr(obj, field.name):
                continue
            if not field.label == FD.LABEL_REPEATED:
                if not field.type == FD.TYPE_MESSAGE:
                    adict[field.name] = getattr(obj, field.name)
                else:
                    value = pb2dict(getattr(obj, field.name))
                    if value:
                        adict[field.name] = value
            else:
                if field.type == FD.TYPE_MESSAGE:
                    adict[field.name] = [pb2dict(v) for v in getattr(obj, field.name)]
                else:
                    adict[field.name] = [v for v in getattr(obj, field.name)]
        return adict
    except Exception as e:
        print(e)
        return obj

context = zmq.Context()
# 服务端绑定推送消息的端口
msg_bind_address = "tcp://*:5557"

def data_forward():
    # socket不能定义在线程外！
    pusher = context.socket(zmq.PUSH)
    pusher.bind(msg_bind_address)
    while True:
        data = my_response_queue.get()
        # 将消息转换成dict格式
        data = pb2dict(data)
        pusher.send_pyobj(data)


if __name__ == '__main__':
    spy = WeChatSpy(response_queue=my_response_queue, key="7d30e1a7903a5a4de12a792ed24ae5ea", logger=logger)
    pid = spy.run(r"D:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    # 注册远程调用的函数, 自己按需增加
    rpc_handler = RPCHandler()
    rpc_handler.register_function(spy.send_text)
    rpc_handler.register_function(spy.get_contacts)
    rpc_handler.register_function(spy.decrypt_image)
    # 转发消息到客户端
    data_forward() 
        


