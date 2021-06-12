import os
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import logging
from .proto import spy_pb2
from .command import *
import subprocess
from queue import Queue
from uuid import uuid4
import sys


if not sys.version >= "3.8":
    logging.error("微信版本过低，请使用Python3.8.x或更高版本")
    exit()


class WeChatSpy:
    def __init__(self, response_queue=None, key: str = None, logger: logging.Logger = None):
        # 付费key
        self.__key = key
        # 日志模块
        if isinstance(logger, logging.Logger):
            # 使用自定义logger
            self.logger = logger
        else:
            # 使用默认logger
            self.logger = logging.getLogger(__file__)
            formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            sh.setLevel(logging.DEBUG)
            self.logger.addHandler(sh)
            self.logger.setLevel(logging.DEBUG)
        # response存放队列
        if isinstance(response_queue, Queue):
            self.__response_queue = response_queue
        else:
            raise Exception("response_queue must be Queue")
        self.pids = []
        self.port2client = dict()
        host = "127.0.0.1"
        port = 9527
        self.__socket_server = socket(AF_INET, SOCK_STREAM)
        self.__socket_server.bind((host, port))
        self.__socket_server.listen(1)
        t_start_server = Thread(target=self.__start_server)
        t_start_server.daemon = True
        t_start_server.name = "spy"
        t_start_server.start()
        current_path = os.path.split(os.path.abspath(__file__))[0]
        helper_path = os.path.join(current_path, "SpyK.exe")
        if not os.path.exists(helper_path):
            self.logger.error("请检查文件 SpyK.exe 是否被误删")
            sys.exit()
        subprocess.Popen(f"{helper_path} 3.0")

    def __start_server(self):
        while True:
            socket_client, client_address = self.__socket_server.accept()
            self.port2client[client_address[1]] = socket_client
            self.logger.debug(f"A WeChat process from {client_address} successfully connected")
            if self.__key:
                self.set_commercial(self.__key, port=client_address[1])
            t_socket_client_receive = Thread(target=self.receive, args=(socket_client, client_address))
            t_socket_client_receive.name = f"wechat {client_address}"
            t_socket_client_receive.daemon = True
            t_socket_client_receive.start()

    def receive(self, socket_client: socket, client_address: tuple):
        recv_bytes = b""
        data_size = 0
        while True:
            try:
                _bytes = socket_client.recv(4096)
            except Exception as e:
                self.port2client.pop(client_address[1])
                response = spy_pb2.Response()
                response.type = WECHAT_DISCONNECT
                response.port = client_address[1]
                self.__response_queue.put(response)
                return self.logger.warning(f"The WeChat process has disconnected: {e}")
            recv_bytes += _bytes
            while True:
                if not data_size:
                    if len(recv_bytes) > 3:
                        data_size = int.from_bytes(recv_bytes[:4], "little")
                    else:
                        break
                elif data_size <= len(recv_bytes) - 4:
                    response = spy_pb2.Response()
                    response.ParseFromString(recv_bytes[4: data_size + 4])
                    response.port = client_address[1]
                    self.__response_queue.put(response)
                    recv_bytes = recv_bytes[data_size + 4:]
                    data_size = 0
                else:
                    break

    def __send(self, request: spy_pb2.Request, port: int = 0, _id: str = None):
        if not port and self.port2client:
            socket_client: socket = list(self.port2client.values())[0]
        elif not (socket_client := self.port2client.get(port)):
            self.logger.error(f"Failure to find socket client by port:{port}")
            return False
        request.id = _id or uuid4().__str__()
        data = request.SerializeToString()
        data_length_bytes = int.to_bytes(len(data), length=4, byteorder="little")
        try:
            socket_client.send(data_length_bytes + data)
            return True
        except Exception as e:
            self.logger.warning(f"The WeChat process {port} has disconnected: {e}")
            return False

    def run(self, wechat: str):
        sp = subprocess.Popen(wechat)
        self.pids.append(sp.pid)
        return sp.pid

    def set_commercial(self, key: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = PROFESSIONAL_KEY
        request.bytes = bytes(key, encoding="utf8")
        return self.__send(request, port, _id)

    def get_account_details(self, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = GET_ACCOUNT_DETAILS
        return self.__send(request, port, _id)

    def get_contacts(self, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = GET_CONTACTS_LIST
        return self.__send(request, port, _id)

    def get_contact_details(self, wxid: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = GET_CONTACT_DETAILS
        request.bytes = bytes(wxid, encoding="utf8")
        return self.__send(request, port, _id)

    def send_text(self, wxid: str, text: str, at_wxid: str = "", port: int = 0, _id: str = None):
        if not wxid.endswith("chatroom"):
            at_wxid = ""
        request = spy_pb2.Request()
        request.type = SEND_TEXT
        text_message = spy_pb2.TextMessage()
        text_message.wxid = wxid
        text_message.wxidAt = at_wxid
        text_message.text = text
        request.bytes = text_message.SerializeToString()
        return self.__send(request, port, _id)

    def send_file(self, wxid: str, file_path: str, port: int = 0, _id: str = None):
        if not os.path.exists(file_path):
            self.logger.error(f"File Not Found {file_path}")
            return False
        if len(file_path.split("\\")) > 8:
            self.logger.error(f"File path is too long: {file_path}")
            return False
        request = spy_pb2.Request()
        request.type = SEND_FILE
        file_message = spy_pb2.FileMessage()
        file_message.wxid = wxid
        file_message.filePath = file_path
        request.bytes = file_message.SerializeToString()
        return self.__send(request, port, _id)

    def user_logout(self, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = USER_LOGOUT
        return self.__send(request, port, _id)

    def accept_new_contact(self, encryptusername: str, ticket: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = ACCEPT_NEW_CONTACT
        application = spy_pb2.ContactApplication()
        application.encryptusername = encryptusername
        application.ticket = ticket
        request.bytes = application.SerializeToString()
        return self.__send(request, port, _id)

    def send_announcement(self, wxid: str, content: str, port: int = 0, _id: str = None):
        if not wxid.endswith("chatroom"):
            return self.logger.warning("Can only send announcements to chatrooms")
        request = spy_pb2.Request()
        request.type = SEND_ANNOUNCEMENT
        text_message = spy_pb2.TextMessage()
        text_message.wxid = wxid
        text_message.text = content
        request.bytes = text_message.SerializeToString()
        return self.__send(request, port, _id)

    def create_chatroom(self, wxid: str, port: int = 0, _id: str = None):
        if len(wxid.split(",")) < 2:
            return self.logger.warning("This function requires at least two wxids separated by ','")
        request = spy_pb2.Request()
        request.type = CREATE_CHATROOM
        request.bytes = bytes(wxid, encoding="utf8")
        return self.__send(request, port, _id)

    def share_chatroom(self, chatroom_wxid: str, wxid: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = SHARE_CHATROOM
        text_message = spy_pb2.TextMessage()
        text_message.wxid = wxid
        text_message.text = chatroom_wxid
        request.bytes = text_message.SerializeToString()
        return self.__send(request, port, _id)

    def remove_chatroom_member(self, chatroom_wxid: str, wxid: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = REMOVE_CHATROOM_MEMBER
        text_message = spy_pb2.TextMessage()
        text_message.wxid = wxid
        text_message.text = chatroom_wxid
        request.bytes = text_message.SerializeToString()
        return self.__send(request, port, _id)

    def remove_contact(self, wxid: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = REMOVE_CONTACT
        request.bytes = bytes(wxid, encoding="utf8")
        return self.__send(request, port, _id)

    def send_mini_program(self, wxid: str, title: str, image_path: str, route: str, app_id: str,
                          username: str, weappiconurl: str, appname: str, port: int = 0, _id: str = None):
        if not os.path.exists(image_path):
            self.logger.error(f"Image Not Found {image_path}")
            return False
        request = spy_pb2.Request()
        request.type = SEND_MINI_PROGRAM
        xml = spy_pb2.XmlMessage()
        xml.wxid = wxid
        xml.title = title
        xml.appId = app_id
        xml.imagePath = image_path
        xml.route = route
        xml.username = username
        xml.weappiconurl = weappiconurl
        xml.appname = appname
        request.bytes = xml.SerializeToString()
        return self.__send(request, port, _id)

    def send_link_card(self, wxid: str, title: str, desc: str, app_id: str,
                       url: str, image_path: str, port: int = 0, _id: str = None):
        if not os.path.exists(image_path):
            self.logger.error(f"Image Not Found {image_path}")
            return False
        request = spy_pb2.Request()
        request.type = SEND_LINK_CARD
        xml = spy_pb2.XmlMessage()
        xml.wxid = wxid
        xml.title = title
        xml.desc = desc
        xml.url = url
        xml.appId = app_id
        xml.imagePath = image_path
        request.bytes = xml.SerializeToString()
        return self.__send(request, port, _id)

    def add_contact(self, wxid: str, chatroom_wxid: str = "", greeting: str = "",
                    add_type: int = 0, port: int = 0, _id: str = None):
        # TODO:
        request = spy_pb2.Request()
        request.cmd = add_type
        request.param1 = wxid
        if add_type == 1 and not chatroom_wxid:
            return
        request.param2 = chatroom_wxid
        request.param3 = greeting
        return self.__send(request, port, _id)

    def get_contact_status(self, wxid: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = GET_CONTACT_STATUS
        request.bytes = bytes(wxid, encoding="utf8")
        return self.__send(request, port, _id)

    def set_chatroom_name(self, wxid: str, name: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = SET_CHATROOM_NAME
        text_message = spy_pb2.TextMessage()
        text_message.wxid = wxid
        text_message.text = name
        request.bytes = text_message.SerializeToString()
        return self.__send(request, port, _id)

    def get_login_qrcode(self, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = GET_LOGIN_QRCODE
        return self.__send(request, port, _id)

    def set_remark(self, wxid: str, remark: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = SET_REMARK
        text_message = spy_pb2.TextMessage()
        text_message.wxid = wxid
        text_message.text = remark
        request.bytes = text_message.SerializeToString()
        return self.__send(request, port, _id)

    def get_group_enter_url(self, wxid: str, url: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = GET_GROUP_ENTER_URL
        text_message = spy_pb2.TextMessage()
        text_message.wxid = wxid
        text_message.text = url
        request.bytes = text_message.SerializeToString()
        return self.__send(request, port, _id)

    def decrypt_image(self, source_file: str, target_file: str, port: int = 0, _id: str = None):
        if not os.path.exists(source_file):
            self.logger.error(f"File Not Found {source_file}")
            return False
        request = spy_pb2.Request()
        request.type = DECRYPT_IMAGE
        file_message = spy_pb2.FileMessage()
        file_message.wxid = source_file
        file_message.filePath = target_file
        request.bytes = file_message.SerializeToString()
        return self.__send(request, port, _id)

    def send_card(self, wxid: str, card_wxid: str, card_nickname: str, port: int = 0, _id: str = None):
        request = spy_pb2.Request()
        request.type = SEND_CARD
        xml = spy_pb2.XmlMessage()
        xml.wxid = wxid
        xml.title = card_nickname
        xml.username = card_wxid
        request.bytes = xml.SerializeToString()
        return self.__send(request, port, _id)
