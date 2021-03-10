from flask import Flask
from ..spy import WeChatSpy
from queue import Queue
from threading import Thread
from ..proto.spy_pb2 import Response, ChatMessage
from ..command import *
from .config import MESSAGE_CALLBACK
import requests


class SpyService(Flask):
    def __init__(self, import_name,
                 static_url_path=None,
                 static_folder="static",
                 static_host=None,
                 host_matching=False,
                 subdomain_matching=False,
                 template_folder="templates",
                 instance_path=None,
                 instance_relative_config=False,
                 root_path=None,
                 key=None):
        self.last_client_count = 0
        self.response_queue = Queue()
        self.client2pid = dict()
        self.client2wxid = dict()
        self.client2login = dict()
        self.client2user_logout = dict()
        self.client2response = dict()
        self.__chat_message = []
        self.spy = WeChatSpy(response_queue=self.response_queue, key=key)
        super().__init__(import_name,
                         static_url_path=static_url_path,
                         static_folder=static_folder,
                         static_host=static_host,
                         host_matching=host_matching,
                         subdomain_matching=subdomain_matching,
                         template_folder=template_folder,
                         instance_path=instance_path,
                         instance_relative_config=instance_relative_config,
                         root_path=root_path)
        t = Thread(target=self.parse)
        t.setDaemon(True)
        t.start()

    def parse(self):
        while True:
            data = self.response_queue.get()
            if data.type == WECHAT_CONNECTED:
                self.client2pid[data.port] = data.pid
                self.client2login[data.port] = "0"
            elif data.type == WECHAT_DISCONNECT:
                self.last_client_count -= 1
            elif data.type == WECHAT_LOGIN:
                self.client2login[data.port] = "1"
            elif data.type == WECHAT_LOGOUT:
                self.client2login[data.port] = "0"
            elif data.type == CHAT_MESSAGE:
                self.__chat_message.append(data)
            elif data.type != HEART_BEAT:
                if data.type == GET_LOGIN_QRCODE and data.code:
                    continue
                elif data.type == GET_CONTACTS_LIST and data.code:
                    continue
                elif data.type == SEND_TEXT and data.code:
                    continue
                elif data.type == SEND_FILE and data.code:
                    continue
                elif data.type == SEND_MINI_PROGRAM and data.code:
                    continue
                elif data.type == SEND_LINK_CARD and data.code:
                    continue
                elif data.type == CREATE_CHATROOM and data.code:
                    continue
                self.client2response[data.id] = data

    def push_message(self):
        while True:
            message_data: Response = self.__chat_message.pop()
            message_port = message_data.port
            chat_message = ChatMessage()
            chat_message.ParseFromString(message_data.bytes)
            post_data = {
                "port": message_port,
                "messages": []
            }
            for message in chat_message.message:
                _from = message.wxidFrom.str  # 消息发送方
                _from_group_member = ""
                if _from.endswith("@chatroom"):  # 群聊消息
                    _from_group_member = message.content.str.split(':\n', 1)[0]  # 群内发言人
                    content = message.content.str.split(':\n', 1)[-1]  # 群聊消息内容
                _file = message.file
                post_data["messages"].append({
                    "type": message.type,
                    "from": _from,
                    "to": message.wxidTo.str,
                    "from_group_member": _from_group_member,
                    "content": message.content.str,
                    "timestamp": message.timestamp,
                    "file": _file
                })
            try:
                requests.post(MESSAGE_CALLBACK, json=post_data)
            except Exception as e:
                print(e)
