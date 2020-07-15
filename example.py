from PyWeChatSpy import WeChatSpy
import requests


contact_dict = {}


def get_reply(data):
    url = f"http://api.douqq.com/?key=&msg={data}"  # key获取地址http://xiao.douqq.com/
    resp = requests.get(url)
    return resp.text


def my_parser(data):
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
    elif data["type"] == 2:
        # 联系人详情
        print(data)
    elif data["type"] == 3:
        # 联系人列表
        for contact in data["data"]:
            print(contact)
    elif data["type"] == 9527:
        spy.logger.warning(data)
    elif data["type"] == 8:
        print(data)


spy = WeChatSpy(parser=my_parser, key="18d421169d93611a5584affac335e690")


if __name__ == '__main__':
    spy.run()

