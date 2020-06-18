from ast import literal_eval
import json
import os
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
from subprocess import Popen, PIPE
from .exceptions import handle_error_code
import logging
import warnings
import re

pattern = '[\u4e00-\u9fa5]'
formatter = logging.Formatter('%(asctime)s [%(threadName)s] %(levelname)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(logging.DEBUG)


class WeChatSpy:
    def __init__(self, parser=None, error_handle=None, multi=False, key=None):
        self.logger = logging.getLogger(__file__)
        self.logger.addHandler(sh)
        self.logger.setLevel(logging.DEBUG)
        # TODO: 异常处理函数
        self.__error_handle = error_handle
        # 是否多开微信PC客户端
        self.__multi = multi
        # 商用key
        self.__key = key
        # socket数据处理函数
        self.__parser = parser
        self.__pid2client = {}
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
            if self.__key:
                data = json.dumps({"code": 9527, "key": self.__key})
                data_length_bytes = int.to_bytes(len(data.encode(encoding="utf8")), length=4, byteorder="little")
                socket_client.send(data_length_bytes + data.encode(encoding="utf8"))
            t_socket_client_receive = Thread(target=self.receive, args=(socket_client, ))
            t_socket_client_receive.name = f"client {client_address[1]}"
            t_socket_client_receive.daemon = True
            t_socket_client_receive.start()

    def receive(self, socket_client):
        data_str = ""
        _data_str = None
        while True:
            try:
                _data_str = socket_client.recv(4096).decode(encoding="utf8", errors="ignore")
            except Exception as e:
                for pid, client in self.__pid2client.items():
                    if client == socket_client:
                        self.__pid2client.pop(pid)
                        return self.logger.warning(f"A WeChat process (PID:{pid}) has disconnected: {e}")
                else:
                    pid = "unknown"
                    return self.logger.warning(f"A WeChat process (PID:{pid}) has disconnected: {e}")
            if _data_str:
                data_str += _data_str
            if data_str and data_str.endswith("*393545857*"):
                for data in data_str.split("*393545857*"):
                    if data:
                        data = literal_eval(data)
                        if not self.__pid2client.get(data["pid"]) and data["type"] == 200:
                            self.__pid2client[data["pid"]] = socket_client
                            self.logger.info(f"A WeChat process (PID:{data['pid']}) successfully connected")
                        if callable(self.__parser):
                            self.__parser(data)
                data_str = ""

    def __send(self, data, pid):
        if pid:
            socket_client = self.__pid2client.get(pid)
        else:
            socket_client_list = list(self.__pid2client.values())
            socket_client = socket_client_list[0] if socket_client_list else None
        if socket_client:
            data = json.dumps(data)
            data_length_bytes = int.to_bytes(len(data.encode(encoding="utf8")), length=4, byteorder="little")
            try:
                socket_client.send(data_length_bytes + data.encode(encoding="utf8"))
            except Exception as e:
                for pid, v in self.__pid2client.items():
                    if v == socket_client:
                        self.__pid2client.pop(pid)
                        return self.logger.warning(f"A WeChat process (PID:{pid}) has disconnected: {e}")
                else:
                    pid = "unknown"
                    return self.logger.warning(f"A WeChat process (PID:{pid}) has disconnected: {e}")

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

    def query_contact_details(self, wxid, chatroom_wxid="", pid=None):
        """
        查询联系人详情
        :param wxid: 联系人wxid
        :param chatroom_wxid:
        :param pid:
        """
        data = {"code": 2, "wxid": wxid, "chatroom_wxid": chatroom_wxid}
        self.__send(data, pid)

    def query_contact_list(self, step=50, pid=None):
        """
        查询联系人详情
        :param step: 每次回调的联系人列表长度
        :param pid:
        :return:
        """
        data = {"code": 3, "step": step}
        self.__send(data, pid)

    def query_chatroom_member(self, wxid, pid=None):
        """
        查询群成员列表
        :param wxid: 群wxid
        :param pid:
        :return:
        """
        data = {"code": 4, "wxid": wxid}
        self.__send(data, pid)

    def send_text(self, wxid, content, at_wxid="", pid=None):
        """
        发送文本消息
        :param wxid: 文本消息接收wxid
        :param content: 文本消息内容
        :param at_wxid: 如果wxid为群wxid且需要@群成员 此参数为被@群成员wxid，以英文逗号分隔
        :param pid:
        """
        if not wxid.endswith("chatroom"):
            at_wxid = ""
        data = {"code": 5, "wxid": wxid, "at_wxid": at_wxid, "content": content}
        self.__send(data, pid)

    def send_image(self, wxid, image_path, pid=None):
        warnings.warn("The function 'send_image' is deprecated, and has been replaced by the function 'send_file'",
                      DeprecationWarning)
        self.send_file(wxid, image_path, pid)

    def send_file(self, wxid, file_path, pid=None):
        """
        发送文件消息
        :param wxid: 文件消息接收wxid
        :param file_path: 文件路径
        :param pid:
        """
        if len(file_path.split("\\")) > 8:
            return self.logger.warning(f"File path is too long: {file_path}")
        if re.findall(pattern, file_path):
            return self.logger.warning(f"Chinese characters are not allowed in file path: {file_path}")
        data = {"code": 6, "wxid": wxid, "file_path": file_path}
        self.__send(data, pid)

    def accept_new_contact(self, encryptusername, ticket, pid=None):
        """
        接受好友请求
        :param encryptusername:
        :param ticket:
        :param pid:
        :return:
        """
        data = {"code": 7, "encryptusername": encryptusername, "ticket": ticket}
        self.__send(data, pid)
        
    def send_announcement(self, wxid, content, pid=None):
        """
        发送群公共
        :param wxid: 群wxid
        :param content: 公告内容
        :param pid:
        :return:
        """
        if not wxid.endswith("chatroom"):
            return self.logger.warning("Can only send announcements to chatrooms")
        data = {"code": 8, "wxid": wxid, "content": content}
        self.__send(data, pid)

    def create_chatroom(self, wxid, pid=None):
        """
        创建群聊
        :param wxid: wxid,以","分隔 至少需要两个
        :param pid:
        :return:
        """
        if len(wxid.split(",")) < 2:
            return self.logger.warning("This function requires at least two wxids separated by ','")
        data = {"code": 9, "wxid": wxid}
        self.__send(data, pid)

    def share_chatroom(self, chatroom_wxid, wxid, pid=None):
        """
        分享群聊邀请链接
        :param chatroom_wxid:
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 10, "wxid": wxid, "chatroom_wxid": chatroom_wxid}
        self.__send(data, pid)

    def remove_chatroom_member(self, chatroom_wxid, wxid, pid=None):
        """
        移除群成员
        :param chatroom_wxid:
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 11, "wxid": wxid, "chatroom_wxid": chatroom_wxid}
        self.__send(data, pid)

    def remove_contact(self, wxid, pid=None):
        """
        移除联系人
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 12, "wxid": wxid}
        self.__send(data, pid)

    def add_contact_from_chatroom(self, chatroom_wxid, wxid, msg, pid=None):
        """
        将群成员添加为好友
        :param chatroom_wxid: 群wxid
        :param wxid: 群成员wxid
        :param msg: 好友申请信息
        :param pid:
        :return:
        """
        data = {"code": 13, "wxid": wxid, "chatroom_wxid": chatroom_wxid, "msg": msg}
        self.__send(data, pid)

    def add_unidirectional_contact_a(self, wxid, msg, pid=None):
        """
        添加单向好友(自己被对方删除)
        :param wxid:
        :param msg: 好友申请信息
        :param pid:
        :return:
        """
        data = {"code": 14, "wxid": wxid, "msg": msg}
        self.__send(data, pid)

    def add_unidirectional_contact_b(self, wxid, pid=None):
        """
        添加单向好友(对方被自己删除)
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 15, "wxid": wxid}
        self.__send(data, pid)

    def check_contact_status(self, wxid, pid=None):
        """
        检查联系人状态
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 16, "wxid": wxid}
        self.__send(data, pid)
