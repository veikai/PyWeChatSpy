from ast import literal_eval
import json
import os
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
from subprocess import Popen, PIPE
from .exceptions import handle_error_code
import logging


formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.DEBUG)


class WeChatSpy:
    def __init__(self, parser=None, error_handle=None, download_image=False, multi=False):
        self.logger = logging.getLogger()
        self.logger.addHandler(sh)
        self.logger.setLevel(logging.DEBUG)
        # 是否下载图片(小于2MB)
        # 该参数为True时 微信会自动下载收到的小于2MB的图片 但会造成图片消息延迟响应
        self.__download_image = download_image
        # TODO: 异常处理函数
        self.__error_handle = error_handle
        # 是否多开微信PC客户端
        self.__multi = multi
        # socket数据处理函数
        self.__parser = parser
        self.__socket_client_dict = {}
        self.__socket_server = socket(AF_INET, SOCK_STREAM)
        self.__socket_server.bind(("127.0.0.1", 9527))
        self.__socket_server.listen(1)
        t_start_server = Thread(target=self.__start_server)
        t_start_server.daemon = True
        t_start_server.name = "socket accept"
        t_start_server.start()

    def add_log_output_file(self, filename="spy.log", mode='a', encoding="utf8", delay=False, level="WARNING"):
        fh = logging.FileHandler(filename, mode=mode, encoding=encoding, delay=delay)
        if level.upper() == "DEBUG":
            fh.setLevel(logging.DEBUG)
        elif level.upper() == "INFO":
            fh.setLevel(logging.INFO)
        elif level.upper() == "WARNING":
            fh.setLevel(logging.WARNING)
        elif level.upper() == "ERROR":
            fh.setLevel(logging.ERROR)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def __start_server(self):
        while True:
            socket_client, client_address = self.__socket_server.accept()
            self.logger.info(f"A WeChat process from {client_address} successfully connected")
            self.__socket_client_dict[client_address[1]] = socket_client
            if self.__download_image:
                self.__send({"code": 1}, client_address[1])
            t_socket_client_receive = Thread(target=self.receive, args=(socket_client, client_address[1]))
            t_socket_client_receive.name = f"client {client_address[1]}"
            t_socket_client_receive.daemon = True
            t_socket_client_receive.start()

    def receive(self, socket_client, client_port):
        data_str = ""
        _data_str = None
        while True:
            try:
                _data_str = socket_client.recv(4096).decode(encoding="utf8", errors="ignore")
            except Exception as e:
                return self.logger.error(e)
            if _data_str:
                data_str += _data_str
            if data_str and data_str.endswith("*393545857*"):
                for data in data_str.split("*393545857*"):
                    if data:
                        data = literal_eval(data)
                        data["client_port"] = client_port
                        if callable(self.__parser):
                            self.__parser(data)
                data_str = ""

    def __send(self, data, client_port):
        if client_port:
            socket_client = self.__socket_client_dict.get(client_port)
        else:
            socket_client_list = list(self.__socket_client_dict.values())
            socket_client = socket_client_list[0] if socket_client_list else None
        if socket_client:
            data = json.dumps(data)
            data_length_bytes = int.to_bytes(len(data.encode(encoding="utf8")), length=4, byteorder="little")
            socket_client.send(data_length_bytes + data.encode(encoding="utf8"))

    def run(self, background=False):
        current_path = os.path.split(os.path.abspath(__file__))[0]
        launcher_path = os.path.join(current_path, "Launcher.exe")
        cmd_str = f"{launcher_path} multi" if self.__multi else launcher_path
        p = Popen(cmd_str, shell=True, stdout=PIPE)
        res_code, err = p.communicate()
        res_code = res_code.decode()
        handle_error_code(res_code)
        if not background:
            while True:
                sleep(86400)

    def send_text(self, wxid, content, at_wxid="", client_port=None):
        """
        发送文本消息
        :param wxid: 文本消息接收wxid
        :param content: 文本消息内容
        :param at_wxid: 如果wxid为群wxid且需要@群成员 此参数为被@群成员wxid，以英文逗号分隔
        :param client_port:
        """
        if not wxid.endswith("chatroom"):
            at_wxid = ""
        data = {"code": 5, "wxid": wxid, "at_wxid": at_wxid, "content": content}
        self.__send(data, client_port)

    def send_image(self, wxid, image_path, client_port=None):
        """
        发送图片消息
        :param wxid: 图片消息接收wxid
        :param image_path: 图片路径
        :param client_port:
        """
        if len(image_path.split("\\")) > 8:
            return self.logger.warning(f"Image path is too long: {image_path}")
        data = {"code": 6, "wxid": wxid, "image_path": image_path}
        self.__send(data, client_port)

    def query_contact_details(self, wxid, chatroom_wxid="", client_port=None):
        """
        查询联系人详情
        :param wxid: 联系人wxid
        :param chatroom_wxid:
        :param client_port:
        """
        data = {"code": 2, "wxid": wxid, "chatroom_wxid": chatroom_wxid}
        self.__send(data, client_port)
