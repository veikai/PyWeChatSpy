from PyWeChatSpy import WeChatSpy
from PyWeChatSpy.command import *
# from lxml import etree
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
        print("-"*10, "微信连接成功", "-"*10)
        # print("-"*10, "展示登录二维码", "-"*10)
        # spy.show_qrcode()
    elif data.type == WECHAT_LOGIN:
        print("-"*10, "微信登录成功", "-"*10)
        spy.get_login_info()
    elif data.type == WECHAT_LOGOUT:
        print("-"*10, "微信登出", "-"*10)
    elif data.type == LOGIN_INFO:
        print("-"*10, "登录信息", "-"*10)
        print(data.login_info.wxid)
        print(data.login_info.nickname)
        print(data.login_info.wechatid)
        print(data.login_info.phone)
        print(data.login_info.profilephoto)
        # 查询联系人列表(付费)
        spy.get_contacts()
    elif data.type == CONTACTS:
        print("-"*10, "联系人列表", "-"*10)
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
        print("-"*10, f"共{len(contact_list)}个联系人,{len(chatroom_list)}个群", "-"*10)
        # print("-"*10, "获取联系人详情(部分付费)", contact_list[5], "-"*10)
        # spy.get_contact_details(contact_list[5], True)
        # print("设置群名称(付费)", chatroom_list[0])
        # spy.set_chatroom_name(chatroom_list[0], "PyWeChatSpy")
        # print("发送群公告", chatroom_list[0])
        # spy.send_announcement(chatroom_list[0], "本条消息由PyWeChatSpy发出(https://zhuanlan.zhihu.com/p/118674498)")
        # print("创建群聊(付费)")
        # spy.create_chatroom(f"{contact_list[1]},{contact_list[2]},{contact_list[3]}")
        # print("-"*10, "获取群成员列表(付费)", chatroom_list[0], "-"*10)
        # spy.get_chatroom_members(chatroom_list[0])
    elif data.type == MESSAGE:
        # 消息
        for message in data.message_list.message:
            if message.type == 1:
                print("-"*10, "文本消息", "-"*10)
                if message.wxid1 == "filehelper":
                    spy.send_text("filehelper", "Hello PyWeChatSpy")
            elif message.type == 3:
                print("-"*10, "图片消息", "-"*10)
            elif message.type == 37:
                print("-"*10, "好友请求消息", "-"*10)
                # 好友请求消息
                # obj = etree.XML(message.content)
                # encryptusername, ticket = obj.xpath("/msg/@encryptusername")[0], obj.xpath("/msg/@ticket")[0]
                # 接收好友请求(付费)
                # spy.accept_new_contact(encryptusername, ticket)
            else:
                print("-"*10, "其他消息", "-"*10)
                return
            print("来源1:", message.wxid1)
            print("来源2:", message.wxid2)
            print("消息头:", message.head)
            print("消息内容:", message.content)
    elif data.type == QRCODE:
        print("-"*10, "登录二维码", "-"*10)
        print(data.qrcode.qrcode)
    elif data.type == CONTACT_EVENT:
        print("-"*10, "联系人事件", "-"*10)
        print(data)
    elif data.type == CHATROOM_MEMBERS:
        print("-"*10, "群成员列表", "-"*10)
        member_list = data.chatroom_member_list
        chatroom_wxid = member_list.wxid
        print(chatroom_wxid)
        for member in member_list.contact:
            print(member.wxid, member.nickname)
            # 添加群成员为好友(付费)
            # 高风险操作 频率较高容易引发微信风控
            # spy.add_contact(
            #     member.wxid,
            #     chatroom_wxid,
            #     "来自PyWeChatSpy(https://zhuanlan.zhihu.com/p/118674498)的问候",
            #     ADD_CONTACT_A)
    elif data.type == CONTACT_DETAILS:
        print("-"*10, "联系人详情", "-"*10)
        for details in data.contact_list.contact:
            print(details.wxid)
            print(details.nickname)
            print(details.wechatid)
            print(details.remark)
            print(details.profilephoto)
            print(details.profilephoto_hd)
            print(details.sex)
            print(details.whats_up)
            print(details.country)
            print(details.province)
            print(details.city)
            print(details.source)
    elif data.type == HEART_BEAT:
        # 心跳
        pass


spy = WeChatSpy(parser=my_proto_parser, key="授权Key", logger=logger)


if __name__ == '__main__':
    spy.run()
