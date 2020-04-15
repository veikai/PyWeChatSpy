from PyWeChatSpy import WeChatSpy
import requests


def get_reply(data):
    url = f"http://api.douqq.com/?key=&msg={data}"  # key获取地址http://xiao.douqq.com/
    resp = requests.get(url)
    return resp.text


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
            if not item["wxid1"].endswith("@chatroom"):
                content = item["content"]
                print(content)
                reply = get_reply(content)
                print(reply)
                spy.send_text(item["wxid1"], reply)
    elif data["type"] == 2:
        print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()

