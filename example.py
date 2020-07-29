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

contact_list = []
chatroom_list = []


def my_proto_parser(data):
    if data.type == WECHAT_CONNECTED:
        print("微信连接成功")
        spy.show_qrcode()
    elif data.type == WECHAT_LOGIN:
        print("微信登录成功")
        spy.get_login_info()
    elif data.type == WECHAT_LOGOUT:
        print("微信登出")
    elif data.type == LOGIN_INFO:
        print("登录信息")
        print(str(data))
        spy.get_contacts()
    elif data.type == CONTACT_LIST:
        print("联系人列表")
        for contact in data.contact_list.contact:
            print(contact.wxid, contact.nickname)
            if contact.wxid.startswith("gh_"):
                # 过滤公众号
                pass
            elif contact.wxid.endswith("chatroom"):
                # 群聊
                chatroom_list.append(contact.wxid)
            else:
                # 普通联系人
                contact_list.append(contact.wxid)
    elif data.type == MESSAGE:
        # 消息
        for message in data.message_list.message:
            if message.type == 1:
                print("文本消息")
            elif message.type == 3:
                print("图片消息")
            else:
                print("其他消息")
            print("来源1:", message.wxid1)
            print("来源2:", message.wxid2)
            print("消息头:", message.head)
            print("消息内容:", message.content)
    elif data.type == QRCODE:
        print(data)


spy = WeChatSpy(parser=my_proto_parser, key="18d421169d93611a5584affac335e690", logger=logger)  # 同步处理
# spy = WeChatSpy(parser=my_parser_async, key="授权Key", logger=logger)  # 异步处理

if __name__ == '__main__':
    spy.run()  # 异步处理