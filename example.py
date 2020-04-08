from PyWeChatSpy import WeChatSpy


def parser(data):
    if data["type"] == 200:
        # 心跳
        pass
    elif data["type"] == 5:
        # 消息
        for item in data["data"]:
            print(item)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()

