from PyWeChatSpy import WeChatSpy
from PyWeChatSpy.command import *
from PyWeChatSpy.proto import spy_pb2
import random
import re
from queue import Queue

my_response_queue = Queue()


def parse():
    while True:
        data = my_response_queue.get()
        if data.type == CHAT_MESSAGE:  # 判断是微信消息数据
            chat_message = spy_pb2.ChatMessage()
            chat_message.ParseFromString(data.bytes)
            for message in chat_message.message:  # 遍历微信消息
                _type = message.type  # 消息类型 1.文本|3.图片...自行探索
                _from = message.wxidFrom.str  # 消息发送方
                _to = message.wxidTo.str  # 消息接收方
                content = message.content.str  # 消息内容
                print(_type, _from, _to, content)
                if _type == 47:
                    if variables['DouTu'][_from]:
                        image_path = f"faces/{random.randint(1, 21)}.jpg"
                        spy.send_file(_from, image_path)


if __name__ == '__main__':
    spy = WeChatSpy(response_queue=my_response_queue)
    spy.run(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    parse()
