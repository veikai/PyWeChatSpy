from PyWeChatSpy import WeChatSpy
from PyWeChatSpy.command import *
import logging


logger = logging.getLogger(__file__)
formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.setLevel(logging.INFO)


def my_proto_parser(data):
    if data.type == WECHAT_CONNECTED:
        print("微信连接成功")
    elif data.type == WECHAT_LOGIN:
        print("微信登录成功")
        spy.query_login_info()
    elif data.type == WECHAT_LOGOUT:
        print("微信登出")
    elif data.type == LOGIN_INFO:
        print("登录信息")
        print(str(data))
        spy.query_contact_list()
    elif data.type == CONTACT_LIST:
        print("联系人列表")
        for contact in data.contact_list.contact:
            print(contact.wxid)
            print(contact.nickname)
    elif data.type == MESSAGE:
        # 消息
        for message in data.message_list.message:
            if message.type == 1:
                print("文本消息")
                print(message.content)
            elif message.type == 3:
                print("图片消息")
                print


spy = WeChatSpy(parser=my_proto_parser, key="18d421169d93611a5584affac335e690", logger=logger)  # 同步处理
# spy = WeChatSpy(parser=my_parser_async, key="授权Key", logger=logger)  # 异步处理

if __name__ == '__main__':
    spy.run()  # 异步处理