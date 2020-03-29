from PyWeChatSpy import WeChatSpy


def parser(data):
    if data["type"] == 1:
        print(data)
    elif data["type"] == 5:
        for i in data["data"]:
            print(i)
    else:
        print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()
