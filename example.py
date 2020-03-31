from PyWeChatSpy import WeChatSpy


def parser(data):
    if data["type"] == 1:
        # 微信登录信息
        print(data)
    elif data["type"] == 5:
        # 微信消息
        for i in data["data"]:
            print(i)
    else:
        print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()
