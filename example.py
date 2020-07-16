from PyWeChatSpy import WeChatSpy
import requests


def get_reply(data):
    url = f"http://api.douqq.com/?key=&msg={data}"  # key获取地址http://xiao.douqq.com/
    resp = requests.get(url)
    return resp.text


def my_parser(data):
    if data["type"] == 1:
        # 登录信息
        print(data)
    elif data["type"] == 2:
        # 联系人详情
        print(data)
    elif data["type"] == 3:
        # 联系人列表
        for contact in data["data"]:
            print(contact)
    elif data["type"] == 4:
        # 群成员列表
        for member in data["data"]:
            print(member)
    elif data["type"] == 5:
        # 消息
        spy.send_file("filehelper", r"D:\顶多\1111.xls")
        for item in data["data"]:
            print(item)
    elif data["type"] == 8:
        # 二维码信息
        print(data)
    elif data["type"] == 203:
        # 微信登出
        print("微信退出登录")
    elif data["type"] == 9527:
        spy.logger.warning(data)


spy = WeChatSpy(parser=my_parser, key="18d421169d93611a5584affac335e690")


if __name__ == '__main__':
    spy.run()
