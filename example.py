from PyWeChatSpy import WeChatSpy
import time


def parser(data):
    if data["type"] != 200: # 过滤心跳
        print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()
    while True:
        print(1)
        spy.send_text("", "")
        time.sleep(100)