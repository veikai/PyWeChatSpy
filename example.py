from PyWeChatSpy import WeChatSpy
import os


def parser(data):
    if data["type"] == 1:
        # 微信登录信息
        print(data)
    elif data["type"] == 5:
        # 微信消息
        for msg in data["data"]:
            print(msg)
            if msg["msg_type"] == 3:
                data_path = msg["data_path"]
                while True:
                    if os.path.exists(data_path):
                        spy.decrypt_image(data_path, "img.jpg")
                        break
    else:
        print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()
