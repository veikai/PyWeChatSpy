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
                print(_from, content)
                if _to == "filehelper":
                    spy.send_text("filehelper", "Hello PyWeChatSpy3.0\n" + content)
                    if content == "image":
                        spy.send_file("filehelper", r"D:\18020891\Pictures\b.jpg")
            elif _type == 3:  # 图片消息
                pass
            elif _type == 49:  # XML报文消息
                print(_from, content)
    elif data.type == ACCOUNT_DETAILS:  # 登录账号详情
        if data.code:
            account_details = spy_pb2.AccountDetails()
            account_details.ParseFromString(data.bytes)
            print(account_details)
            spy.get_contacts()  # 获取联系人列表
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
                    member_count = contact.groupMemberList.memberCount  # 群成员数量
                    print(member_count)
                    for group_member in contact.groupMemberList.groupMember:
                        member_wxid = group_member.wxid  # 群成员wxid
                        print(member_wxid)
        else:
            logger.error(data.message)
    else:
        print(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=my_proto_parser, key="18d421169d93611a5584affac335e690 ", logger=logger)
    spy.run(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    while True:
        cmd = int(input())
        print(cmd)
        if cmd == ACCOUNT_DETAILS:
            spy.get_account_details()
