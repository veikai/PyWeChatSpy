from ast import literal_eval
from ctypes import cdll, c_char_p
import json
import os
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import winreg

__version__ = "1.0.0.2"


class WeChatSpy:
    def __init__(self, port=9527, parser=None, error_handle=None):
        self.pid = 0
        self.port = port
        self.parser = parser
        self.error_handle = error_handle
        self.__package_path = os.path.split(os.path.abspath(__file__))[0]
        self.__helper = cdll.LoadLibrary(self.__package_path + "\\InjectHelper.dll")
        self.socket_server_handle = socket(AF_INET, SOCK_STREAM)
        self.socket_client_handle = None
        self.login = False
        t_start_server = Thread(target=self.__start_server)
        t_start_server.daemon = True
        t_start_server.start()

    def __start_server(self):
        self.socket_server_handle.bind(("127.0.0.1", self.port))
        self.socket_server_handle.listen(5)
        self.socket_client_handle, client_address = self.socket_server_handle.accept()
        data_str = ""
        while True:
            _data_str = self.socket_client_handle.recv(4096).decode(encoding="utf8", errors="ignore")
            if _data_str:
                data_str += _data_str
            if data_str and data_str.endswith("*393545857*"):
                for data in data_str.split("*393545857*"):
                    if data:
                        data = literal_eval(data)
                        if data["type"] == 1:
                            self.login = True
                        if callable(self.parser):
                            self.parser(data)
                data_str = ""

    def run(self):
        handle = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Tencent\WeChat',
            0,
            (winreg.KEY_WOW64_64KEY + winreg.KEY_READ)
        )
        reg_wechat_path, _type = winreg.QueryValueEx(handle, "InstallPath")
        reg_wechat_version, _type = winreg.QueryValueEx(handle, "Version")
        dll_path = os.path.join(self.__package_path, str(reg_wechat_version), "WeChatSpy.dll")
        if not os.path.exists(dll_path):
            print("微信版本不受支持")
            return
        wechat_path = os.path.join(reg_wechat_path, "WeChat.exe")
        self.pid = self.__helper.OpenAndInject(
            c_char_p(wechat_path.encode(encoding="gbk")),
            c_char_p(dll_path.encode(encoding="gbk"))
        )

    def __send(self, data):
        data = json.dumps(data)
        data_length_bytes = int.to_bytes(len(data.encode(encoding="utf8")), length=4, byteorder="little")
        self.socket_client_handle.send(data_length_bytes + data.encode(encoding="utf8"))

    def send_text(self, wxid, content, at_wxid=""):
        """
        :param wxid: 文本消息接收wxid
        :param content: 文本消息内容
        :param at_wxid: 如果wxid为群wxid且需要@群成员 此参数为被@群成员wxid 否则传空字符串
        """
        data = {"code": 5, "wxid": wxid, "at_wxid": at_wxid, "content": content}
        self.__send(data)

    def send_image(self, wxid, image_path):
        """
        :param wxid: 图片消息接收wxid
        :param image_path: 图片路径
        """
        data = {"code": 6, "wxid": wxid, "image_path": image_path}
        self.__send(data)