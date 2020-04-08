from PyWeChatSpy import WeChatSpy


def parser(data):
    print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()

