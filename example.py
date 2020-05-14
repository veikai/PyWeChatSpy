from PyWeChatSpy import WeChatSpy
from lxml import etree
import requests


contact_dict = {}


def get_reply(data):
    url = f"http://api.douqq.com/?key=&msg={data}"  # key获取地址http://xiao.douqq.com/
    resp = requests.get(url)
    return resp.text


def parser(data):
    if data["type"] == 1:
        # 登录信息
        print(data)
        # 查询联系人列表
        # spy.query_contact_list()
    elif data["type"] == 203:
        # 微信登出
        print("微信退出登录")
    elif data["type"] == 5:
        # 消息
        for item in data["data"]:
            print(item)
            if item["msg_type"] == 37:
                # 好友请求消息
                obj = etree.XML(item["content"])
                encryptusername, ticket = obj.xpath("/msg/@encryptusername")[0], obj.xpath("/msg/@ticket")[0]
                # spy.accept_new_contact(encryptusername, ticket)
    elif data["type"] == 2:
        # 联系人详情
        print(data)
    elif data["type"] == 3:
        # 联系人列表
        for contact in data["data"]:
            print(contact)
    elif data["type"] == 9527:
        spy.logger.warning(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.run()
