from PyWeChatSpy import WeChatSpy
import requests


def get_reply(data):
    url = f"http://api.douqq.com/?key=&msg={data}"  # key获取地址http://xiao.douqq.com/
    resp = requests.get(url)
    return resp.text


def parser(data):
    if data["type"] == 1:
        # 登录信息
        print(data)
    elif data["type"] == 203:
        # 微信登出
        print("微信退出登录")
    elif data["type"] == 5:
        # 消息
        for item in data["data"]:
            print(item)
            wxid1, wxid2 = item["wxid1"], item.get("wxid2")
            spy.query_contact_details(wxid1)
            if wxid1.endswith("chatroom") and wxid2:
                spy.query_contact_details(wxid2, wxid1)
    elif data["type"] == 2:
        # 联系人信息
        print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()

