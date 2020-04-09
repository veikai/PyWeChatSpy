from PyWeChatSpy import WeChatSpy


def parser(data):
    if data["type"] == 1:
        print(data)
    elif data["type"] == 200:
        # 心跳
        pass
    elif data["type"] == 203:
        print("微信退出登录")
    elif data["type"] == 5:
        # 消息
        for item in data["data"]:
            print(item)
            if item["msg_type"] == 1:
                spy.send_text("filehelper", item["content"])


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser, download_image=True)
    spy.run()

