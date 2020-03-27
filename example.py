from PyWeChatSpy import WeChatSpy
import time


def parser(data):
    print(data)


if __name__ == '__main__':
    wcs = WeChatSpy(parser=parser)
    wcs.run()
    while True:
        print(1)
        if wcs.login:
            print(2)
            # wcs.send_text("19163000057@chatroom", "发送测试🤔")
            print(3)
        time.sleep(10)