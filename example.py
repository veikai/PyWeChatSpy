from PyWeChatSpy import WeChatSpy
import logging


logger = logging.getLogger(__file__)
formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.setLevel(logging.INFO)


def my_parser_async(data):
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
        for item in data["data"]:
            print(item)
    elif data["type"] == 8:
        # 二维码信息
        print(data)
    elif data["type"] == 202:
        # 微信登录
        print("微信登录")
        spy.query_login_info()
    elif data["type"] == 203:
        # 微信登出
        print("微信退出登录")


def my_parser_sync(data):
    if data["type"] == 100:
        qrcode = spy.show_qrcode()
        print(qrcode)
    if data["type"] == 202:
        # 微信登录
        print("微信登录")
        login_info = spy.query_login_info()
        print(login_info)
        contact_info = spy.query_contact_list()
        for contact in contact_info["data"]:
            print(contact)
            details = spy.query_contact_details(contact["wxid"])
            print(details)
            break
        print(contact_info["data"][2])
        status = spy.check_contact_status(contact_info["data"][2]["wxid"])
        print(status)


spy = WeChatSpy(parser=my_parser_sync, key="授权Key", logger=logger)


if __name__ == '__main__':
    spy.run(_async=False)
