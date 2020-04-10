from ast import literal_eval
import json
import os
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

__version__ = "1.0.1.2"


class WeChatSpy:
    def __init__(self, port=9527, parser=None, error_handle=None, download_image=False, multi=False):
        # 是否下载图片(小于2MB)
        # 该参数为True时 微信会自动下载收到的小于2MB的图片 但会造成图片消息延迟响应
        self.__download_image = download_image
        # TODO: 异常处理函数
        self.__error_handle = error_handle
        # 是否多开微信PC客户端
        self.__multi = multi
        # socket数据处理函数
        self.__parser = parser
        # socket端口
        self.__port = port
        self.__socket_client_handle = None
        self.__socket_server_handle = socket(AF_INET, SOCK_STREAM)
        self.login = False
        self.pid = 0

    def __start_server(self):
        self.__socket_server_handle.bind(("127.0.0.1", self.__port))
        self.__run_wechat()
        self.__socket_server_handle.listen(1)
        self.__socket_client_handle, client_address = self.__socket_server_handle.accept()
        if self.__download_image:
            self.__send({"code": 1})
        data_str = ""
        while True:
            _data_str = self.__socket_client_handle.recv(4096).decode(encoding="utf8", errors="ignore")
            if _data_str:
                data_str += _data_str
            if data_str and data_str.endswith("*393545857*"):
                for data in data_str.split("*393545857*"):
                    if data:
                        data = literal_eval(data)
                        if not self.login and data["type"] == 1:
                            self.login = True
                        elif self.login and data["type"] == 203:
                            self.login = False
                        if callable(self.__parser):
                            self.__parser(data)
                data_str = ""

    def __run_wechat(self):
        current_path = os.path.split(os.path.abspath(__file__))[0]
        launcher_path = os.path.join(current_path, "Launcher.exe")
        os.system(launcher_path + " multi") if self.__multi else os.system(launcher_path)

    def __send(self, data):
        data = json.dumps(data)
        data_length_bytes = int.to_bytes(len(data.encode(encoding="utf8")), length=4, byteorder="little")
        self.__socket_client_handle.send(data_length_bytes + data.encode(encoding="utf8"))

    def run(self, background=False):
        if background:
            t_start_server = Thread(target=self.__start_server)
            t_start_server.daemon = True
            t_start_server.start()
        else:
            self.__start_server()

    def send_text(self, wxid, content, at_wxid=""):
        """
        发送文本消息
        :param wxid: 文本消息接收wxid
        :param content: 文本消息内容
        :param at_wxid: 如果wxid为群wxid且需要@群成员 此参数为被@群成员wxid，以英文逗号分隔
        """
        if not wxid.endswith("chatroom"):
            at_wxid = ""
        data = {"code": 5, "wxid": wxid, "at_wxid": at_wxid, "content": content}
        self.__send(data)

    def send_image(self, wxid, image_path):
        """
        发送图片消息
        :param wxid: 图片消息接收wxid
        :param image_path: 图片路径
        """
        data = {"code": 6, "wxid": wxid, "image_path": image_path}
        self.__send(data)

    def query_contact_details(self, wxid):
        """
        查询联系人详情
        :param wxid: 联系人wxid
        """
        data = {"code": 2, "wxid": wxid}
        self.__send(data)
