from flask import Flask
from .spy import WeChatSpy
from queue import Queue
from threading import Thread
from .command import *


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
        self.clients = []
        self.client2pid = dict()
        self.client2wxid = dict()
        self.client2login = dict()
        self.client2account = dict()
        self.response_queue = Queue()
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
                self.clients.append(data.port)
                self.client2pid[data.port] = data.pid
                self.client2login[data.port] = "0"
            elif data.type == WECHAT_LOGIN:
                self.client2login[data.port] = "1"
            elif data.type == WECHAT_LOGOUT:
                self.client2login[data.port] = "0"
            elif data.type == ACCOUNT_DETAILS:
                self.client2account[data.port] = data.bytes
