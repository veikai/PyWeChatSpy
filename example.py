from PyWeChatSpy import WeChatSpy


def parser(data):
    if data["type"] != 200:
        print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()

