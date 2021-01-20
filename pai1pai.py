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
                if _type == 10000:  # 判断是微信拍一拍系统提示
                    # 因为微信系统消息很多 因此需要用正则匹配消息内容进一步过滤拍一拍提示
                    m = re.search('".*" 拍了拍我', content)
                    if m:  # 搜索到了匹配的字符串 判断为拍一拍
                        image_path = f"images/{random.randint(1, 7)}.jpg"  # 随机选一张回复用的图片
                        spy.send_file(_from, image_path)  # 发送图片


if __name__ == '__main__':
    spy = WeChatSpy(response_queue=my_response_queue)
    spy.run(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    parse()
