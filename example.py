from PyWeChatSpy import WeChatSpy
from PyWeChatSpy.command import *
from lxml import etree
import requests
import time
import logging
from PyWeChatSpy.proto import spy_pb2
import base64
import os


logger = logging.getLogger(__file__)
formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.setLevel(logging.INFO)

groups = []
WECHAT_PROFILE = r"D:\18020891\Documents\WeChat Files"


def my_proto_parser(data):
    if data.type == PROFESSIONAL_KEY:
        if not data.code:
            logger.error(data.message)
    elif data.type == WECHAT_CONNECTED:  # 微信接入
        pass
    elif data.type == HEART_BEAT:  # 心跳
        pass
    elif data.type == WECHAT_LOGIN:  # 微信登录
        spy.get_account_details()  # 获取登录账号详情
    elif data.type == WECHAT_LOGOUT:  # 微信登出
        pass
    elif data.type == CHAT_MESSAGE:  # 微信消息
        chat_message = spy_pb2.ChatMessage()
        chat_message.ParseFromString(data.bytes)
        for message in chat_message.message:
            _type = message.type  # 消息类型 1.文本|3.图片...自行探索
            _from = message.wxidFrom.str  # 消息发送方
            _to = message.wxidTo.str  # 消息接收方
            content = message.content.str  # 消息内容
            image_overview_size = message.imageOverview.imageSize  # 图片缩略图大小
            image_overview_bytes = message.imageOverview.imageBytes  # 图片缩略图数据
            # with open("img.jpg", "wb") as wf:
            #     wf.write(image_overview_bytes)
            overview = message.overview  # 消息缩略
            timestamp = message.timestamp  # 消息时间戳
            if _type == 1:  # 文本消息
                print(_from, _to, content)
                if _to == "filehelper":
                    spy.send_text("filehelper", "Hello PyWeChatSpy3.0\n" + content)
                    if content == "image":
                        spy.send_file("filehelper", r"D:\18020891\Pictures\b.jpg")
            elif _type == 3:  # 图片消息
                file_path = message.file
                print(_from, _to, content, file_path)
                file_path = os.path.join(WECHAT_PROFILE, file_path)
                time.sleep(10)
                spy.decrypt_image(file_path, "a.jpg")
            elif _type == 49:  # XML报文消息
                print(_from, content)
    elif data.type == ACCOUNT_DETAILS:  # 登录账号详情
        if data.code:
            account_details = spy_pb2.AccountDetails()
            account_details.ParseFromString(data.bytes)
            print(account_details)
            # spy.get_contacts()  # 获取联系人列表
        else:
            logger.warning(data.message)
    elif data.type == CONTACTS_LIST:  # 联系人列表
        if data.code:
            contacts_list = spy_pb2.Contacts()
            contacts_list.ParseFromString(data.bytes)
            for contact in contacts_list.contactDetails:
                wxid = contact.wxid.str  # 联系人wxid
                nickname = contact.nickname.str  # 联系人昵称
                remark = contact.remark.str  # 联系人备注
                print(wxid, nickname, remark)
                if wxid.endswith("chatroom"):  # 群聊
                    groups.append(wxid)
            wxid = groups.pop()
            print(wxid)
            spy.get_contact_details("20646587964@chatroom")
        else:
            logger.error(data.message)
    elif data.type == CONTACT_DETAILS:
        if data.code:
            contact_details_list = spy_pb2.Contacts()
            contact_details_list.ParseFromString(data.bytes)
            for contact_details in contact_details_list.contactDetails:
                wxid = contact_details.wxid.str  # 联系人wxid
                nickname = contact_details.nickname.str  # 联系人昵称
                remark = contact_details.remark.str  # 联系人备注
                if wxid.endswith("chatroom"):  # 判断是否为群聊
                    group_member_list = contact_details.groupMemberList  # 群成员列表
                    member_count = group_member_list.memberCount  # 群成员数量
                    for group_member in group_member_list.groupMember:  # 遍历群成员
                        member_wxid = group_member.wxid
                        member_nickname = group_member.nickname
                        print(member_wxid, member_nickname)
                    pass
        else:
            logger.error(data.message)
    elif data.type == GET_CONTACTS_LIST and not data.code:
        logger.error(data.message)
    elif data.type == CREATE_GROUP_CALLBACK:  # 创建群聊回调
        callback = spy_pb2.CreateGroupCallback()
        callback.ParseFromString(data.bytes)
        print(callback)
    elif data.type == GROUP_MEMBER_DETAILS:  # 群成员详情
        group_member_details = spy_pb2.GroupMemberDetails()
        group_member_details.ParseFromString(data.bytes)
        print(group_member_details)
    elif data.type == GROUP_MEMBER_EVENT:
        group_member_event = spy_pb2.GroupMemberEvent()
        group_member_event.ParseFromString(data.bytes)
        print(group_member_event)
    else:
        print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=my_proto_parser, key="18d421169d93611a5584affac335e690", logger=logger)
    spy.run(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    while True:
        cmd = int(input())
        print(cmd)
        if cmd == ACCOUNT_DETAILS:
            spy.get_account_details()
        elif cmd == SEND_TEXT:
            spy.send_text("20646587964@chatroom", "@Hello PyWeChatSpy", "wxid_wbgerrlnz6kt22", 0)
        elif cmd == SET_REMARK:
            spy.set_remark("wxid_wbgerrlnz6kt22", "备注测试")
        elif cmd == SEND_MINI_PROGRAM:
            image_path = r"D:\18020891\Pictures\b.jpg"
            spy.send_mini_program(
                "20646587964@chatroom",
                "小程序发送测试",
                image_path,
                "packageFourth/pages/fourth/fourth.html?productId=12122946310&amp;shop=0000000000&amp;union=Ivcomvrb",
                "mainApp",
                "gh_1d1e15e90afc@app",
                "http://mmbiz.qpic.cn/mmbiz_png/iclBO8bMDwtibgxxBCjYPT74TItA7iamnZST3WNLYv1RVw4LqIBEWLq657C8oR1kXY7Y2N0V8QAibibcPyicIfcT7c3g/640?wx_fmt=png&amp;wxfrom=200",
                "1234567",
                0
            )
        elif cmd == SEND_LINK_CARD:
            spy.send_link_card(
                "20646587964@chatroom",
                "咖啡发送测试",
                "屠龙宝刀点击就送",
                "wx59cc372381201d39",
                "http://www.baidu.com",
                r"D:\18020891\Documents\WeChat Files\wxid_ekxxwtu6212f21\FileStorage\Cache\2020-12\af3fff6dff2e35b4d85af849ac216034_t.jpg",
                0)
        elif cmd == CREATE_CHATROOM:
            spy.create_chatroom("wxid_2mh1kb172f7l21,wxid_z5xpxbzzqxih21", 0)
        elif cmd == SET_CHATROOM_NAME:
            spy.set_chatroom_name("20646587964@chatroom", "PyWeChatSpy交流群")
        elif cmd == GET_CONTACT_STATUS:
            # spy.get_contact_status("wxid_wbgerrlnz6kt22")
            spy.get_contact_status("wxid_z5xpxbzzqxih21")
        elif cmd == SEND_FILE:
            spy.send_file("20646587964@chatroom", r"D:\18020891\Pictures\b.jpg")
