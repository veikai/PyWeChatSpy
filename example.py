from PyWeChatSpy import WeChatSpy
from PyWeChatSpy.command import *
from lxml import etree
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from PyWeChatSpy.proto import spy_pb2
import os
import shutil
from queue import Queue
from PyWeChatSpy.games.truth_or_dare import TruthOrDare


logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.INFO)
fh = TimedRotatingFileHandler("spy.log", when="midnight")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)


WECHAT_PROFILE = rf"C:\Users\{os.environ['USERNAME']}\Documents\WeChat Files"
PATCH_PATH = rf"C:\Users\{os.environ['USERNAME']}\AppData\Roaming\Tencent\WeChat\patch"
if not os.path.exists(WECHAT_PROFILE):
    logger.error("请先设置计算机用户名，并完善WECHAT_PROFILE和PATCH_PATH")
    exit()
if os.path.isdir(PATCH_PATH):
    shutil.rmtree(PATCH_PATH)
if not os.path.exists(PATCH_PATH):
    with open(PATCH_PATH, "a") as wf:
        wf.write("")
my_response_queue = Queue()
spy = WeChatSpy(response_queue=my_response_queue, key="ab28d8c4768ab3bc2ba86841313f6e32", logger=logger)
tod = TruthOrDare(spy)


def pop_response():
    while True:
        data = my_response_queue.get()
        handle_response(data)


def handle_response(data):
    if data.type == PROFESSIONAL_KEY:
        if not data.code:
            logger.warning(data.message)
    elif data.type == WECHAT_CONNECTED:  # 微信接入
        print(f"微信客户端已接入 port:{data.port}")
        time.sleep(1)
        # spy.get_login_qrcode()  # 获取登录二维码
    elif data.type == HEART_BEAT:  # 心跳
        pass
    elif data.type == WECHAT_LOGIN:  # 微信登录
        print("微信登录")
        spy.get_account_details()  # 获取登录账号详情
    elif data.type == WECHAT_LOGOUT:  # 微信登出
        print("微信登出")
    elif data.type == CHAT_MESSAGE:  # 微信消息
        chat_message = spy_pb2.ChatMessage()
        chat_message.ParseFromString(data.bytes)
        for message in chat_message.message:
            _type = message.type  # 消息类型 1.文本|3.图片...自行探索
            _from = message.wxidFrom.str  # 消息发送方
            _to = message.wxidTo.str  # 消息接收方
            content = message.content.str  # 消息内容
            _from_group_member = ""
            if _from.endswith("@chatroom"):  # 群聊消息
                _from_group_member = message.content.str.split(':\n', 1)[0]  # 群内发言人
                content = message.content.str.split(':\n', 1)[-1]  # 群聊消息内容
            image_overview_size = message.imageOverview.imageSize  # 图片缩略图大小
            image_overview_bytes = message.imageOverview.imageBytes  # 图片缩略图数据
            # with open("img.jpg", "wb") as wf:
            #     wf.write(image_overview_bytes)
            overview = message.overview  # 消息缩略
            timestamp = message.timestamp  # 消息时间戳
            if _type == 1:  # 文本消息
                print(_from, _to, _from_group_member, content)
                if _to == "filehelper":
                    spy.send_text("filehelper", "Hello PyWeChatSpy3.0\n" + content)
                    time.sleep(2)
                    spy.send_file("filehelper", r"D:\18020891\Pictures\b.jpg")
            elif _type == 3:  # 图片消息
                file_path = message.file
                file_path = os.path.join(WECHAT_PROFILE, file_path)
                time.sleep(10)
                # spy.decrypt_image(file_path, "a.jpg")
            elif _type == 43:  # 视频消息
                pass
            elif _type == 49:  # XML报文消息
                print(_from, _to, message.file)
                xml = etree.XML(content)
                xml_type = xml.xpath("/msg/appmsg/type/text()")[0]
                if xml_type == "5":
                    xml_title = xml.xpath("/msg/appmsg/title/text()")[0]
                    print(xml_title)
                    if xml_title == "邀请你加入群聊":
                        url = xml.xpath("/msg/appmsg/url/text()")[0]
                        print(url)
                        time.sleep(1)
                        spy.get_group_enter_url(_from, url)
            elif _type == 37:  # 好友申请
                print("新的好友申请")
                obj = etree.XML(message.content.str)
                encryptusername, ticket = obj.xpath("/msg/@encryptusername")[0], obj.xpath("/msg/@ticket")[0]
                spy.accept_new_contact(encryptusername, ticket)  # 接收好友请求
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
            for contact in contacts_list.contactDetails:  # 遍历联系人列表
                wxid = contact.wxid.str  # 联系人wxid
                nickname = contact.nickname.str  # 联系人昵称
                remark = contact.remark.str  # 联系人备注
                print(wxid, nickname, remark)
            # spy.get_contact_details("20646587964@chatroom")  # 获取群聊详情
        else:
            logger.error(data.message)
    elif data.type == CONTACT_DETAILS:
        if data.code:
            contact_details_list = spy_pb2.Contacts()
            contact_details_list.ParseFromString(data.bytes)
            for contact_details in contact_details_list.contactDetails:  # 遍历联系人详情
                wxid = contact_details.wxid.str  # 联系人wxid
                nickname = contact_details.nickname.str  # 联系人昵称
                remark = contact_details.remark.str  # 联系人备注
                if wxid.endswith("chatroom"):  # 判断是否为群聊
                    group_member_list = contact_details.groupMemberList  # 群成员列表
                    member_count = group_member_list.memberCount  # 群成员数量
                    for group_member in group_member_list.groupMember:  # 遍历群成员
                        member_wxid = group_member.wxid  # 群成员wxid
                        member_nickname = group_member.nickname  # 群成员昵称
                        # print(member_wxid, member_nickname)
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
        # print(group_member_details)
    elif data.type == GROUP_MEMBER_EVENT:  # 群成员进出事件
        group_member_event = spy_pb2.GroupMemberEvent()
        group_member_event.ParseFromString(data.bytes)
        # print(group_member_event)
    elif data.type == LOGIN_QRCODE:  # 登录二维码
        qrcode = spy_pb2.LoginQRCode()
        qrcode.ParseFromString(data.bytes)
        with open("qrcode.png", "wb") as _wf:
            _wf.write(qrcode.qrcodeBytes)
    elif data.type == GROUP_ENTER_URL:  # 进群链接
        group_enter_url = spy_pb2.GroupEnterUrl()
        group_enter_url.ParseFromString(data.bytes)
        print(group_enter_url)
        # 进群直接post请求链接
        # try:
        #     requests.post(group_enter_url.url)
        # except requests.exceptions.InvalidSchema:
        #     pass
        # except Exception as e:
        #     logger.error(f"进群失败：{e}")
    elif data.type == SEND_TEXT_CALLBACK:
        print("发送文本回调")
        print(data)
        print(data.code)
    elif data.type == SEND_XML_CALLBACK:
        print("发送xml回调")
        print(data)
        print(data.code)
    elif data.type == SEND_IMAGE_CALLBACK:
        print("发送图片回调")
        print(data)
        print(data.code)
    else:
        print(data)


if __name__ == '__main__':
    pid = spy.run(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    pop_response()
