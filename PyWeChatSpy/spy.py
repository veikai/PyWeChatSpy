import os
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
from subprocess import Popen, PIPE
from .exceptions import handle_error_code, ParserError
import logging
import warnings
from uuid import uuid4
from .proto import spy_pb2
from .command import *


class WeChatSpy:
    def __init__(self,
                 parser=None,
                 multi: bool = False,
                 key: str = None,
                 logger: logging.Logger = None,
                 host: str = "127.0.0.1",
                 port: int = 9527
                 ):
        # 是否多开微信PC客户端
        self.__multi = multi
        # 商用key
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
        # socket数据处理函数
        if callable(parser):
            if parser.__code__.co_argcount == 1:
                self.__parser = parser
            else:
                raise ParserError("The parser function can have only one argument")
        else:
            raise ParserError("Parser must be callable")
        self.__port2client = {}
        self.__socket_server = socket(AF_INET, SOCK_STREAM)
        self.__socket_server.bind((host, port))
        self.__socket_server.listen(1)
        t_start_server = Thread(target=self.__start_server)
        t_start_server.daemon = True
        t_start_server.name = "socket accept"
        t_start_server.start()

    def __start_server(self):
        while True:
            socket_client, client_address = self.__socket_server.accept()
            self.logger.info(f"A WeChat process from {client_address} successfully connected")
            if self.__key:
                request = spy_pb2.Request()
                request.cmd = SYSTEM
                request.content = self.__key
                request.uuid = ""
                data = request.SerializeToString()
                data_length_bytes = int.to_bytes(len(data), length=4, byteorder="little")
                socket_client.send(data_length_bytes + data)
            t_socket_client_receive = Thread(target=self.receive, args=(socket_client, client_address))
            t_socket_client_receive.name = f"receive {client_address}"
            t_socket_client_receive.daemon = True
            t_socket_client_receive.start()

    def receive(self, socket_client: socket, client_address: tuple):
        recv_byte = b""
        data_size = 0
        while True:
            try:
                _bytes = socket_client.recv(4096)
            except Exception as e:
                return self.logger.warning(f"The WeChat process has disconnected: {e}")
            recv_byte += _bytes
            while True:
                if not data_size:
                    if len(recv_byte) > 3:
                        data_size = int.from_bytes(recv_byte[:4], "little")
                    else:
                        break
                elif data_size <= len(recv_byte) - 4:
                    data_byte = recv_byte[4: data_size + 4]
                    response = spy_pb2.Response()
                    response.ParseFromString(data_byte)
                    recv_byte = recv_byte[data_size + 4:]
                    data_size = 0
                    if response.type == SYSTEM:
                        if response.info:
                            self.logger.info(f"{response.info}")
                        elif response.warning:
                            self.logger.warning(f"{response.warning}")
                        elif response.error:
                            self.logger.error(f"{response.error}")
                    else:
                        t = Thread(target=self.__parser, args=(response,))
                        t.name = f"parse {client_address}"
                        t.daemon = True
                        t.start()

    def __send(self, request: spy_pb2.Request, port: int = 0):
        if not port and self.__port2client:
            socket_client = list(self.__port2client.values())[0]
        else:
            socket_client = self.__port2client.get(port)
        if not socket_client:
            self.logger.error(f"Socket client(port: {port}) not found")
            return
        request.uuid = uuid4().__str__()
        data = request.SerializeToString()
        data_length_bytes = int.to_bytes(len(data), length=4, byteorder="little")
        try:
            socket_client.send(data_length_bytes + data)
        except Exception as e:
            return self.logger.warning(f"The WeChat process {port} has disconnected: {e}")

    def run(self, background: bool = False):
        current_path = os.path.split(os.path.abspath(__file__))[0]
        launcher_path = os.path.join(current_path, "Launcher.exe")
        cmd_str = f"{launcher_path} multi" if self.__multi else launcher_path
        p = Popen(cmd_str, shell=True, stdout=PIPE)
        res_code, err = p.communicate()
        res_code = res_code.decode()
        handle_error_code(res_code)
        pid = int(res_code)
        if not background:
            while True:
                sleep(86400)
        return pid

    def get_login_info(self, pid: int = 0):
        """
        获取当前登录信息
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = LOGIN_INFO
        return self.__send(request, pid)

    def query_login_info(self, pid: int = 0):
        warnings.warn(
            "The function 'query_login_info' is deprecated, and has been replaced by the function 'get_login_info'",
            DeprecationWarning)
        return self.get_login_info(pid)

    def get_contacts(self, pid: int = 0):
        """
        获取联系人详情
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = CONTACTS
        return self.__send(request, pid)

    def query_contact_list(self, pid: int = 0):
        warnings.warn(
            "The function 'query_contact_list' is deprecated, and has been replaced by the function 'get_contact_list'",
            DeprecationWarning)
        return self.get_contacts(pid)

    def get_contact_details(self, wxid: str, update: bool = False, pid: int = 0):
        """
        获取联系人详情
        :param wxid: 联系人wxid
        :param update: 是否更新最新详情(需请求微信服务器 速度较慢)
        :param pid:
        """
        request = spy_pb2.Request()
        request.cmd = CONTACT_DETAILS
        request.wxid = wxid
        request.update = 1 if update else 0
        return self.__send(request, pid)

    def query_contact_details(self, wxid: str, update: bool = False, pid: int = 0):
        warnings.warn(
            "The function 'query_contact_details' is deprecated, "
            "and has been replaced by the function 'get_contact_details'", DeprecationWarning)
        return self.get_contact_details(wxid, update, pid)

    def get_chatroom_members(self, wxid: str, pid: int = 0):
        """
        获取群成员列表
        :param wxid: 群wxid
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = CHATROOM_MEMBERS
        request.wxid = wxid
        return self.__send(request, pid)

    def query_chatroom_member(self, wxid: str, pid: int = 0):
        warnings.warn(
            "The function 'query_chatroom_member' is deprecated, "
            "and has been replaced by the function 'get_chatroom_members'", DeprecationWarning)
        return self.get_chatroom_members(wxid, pid)

    def send_text(self, wxid: str, content: str, at_wxid: str = "", pid: int = 0):
        """
        发送文本消息
        :param wxid: 文本消息接收wxid
        :param content: 文本消息内容
        :param at_wxid: 如果wxid为群wxid且需要@群成员 此参数为被@群成员wxid，以英文逗号分隔
        :param pid:
        """
        if not wxid.endswith("chatroom"):
            at_wxid = ""
        request = spy_pb2.Request()
        request.cmd = SEND_TEXT
        request.wxid = wxid
        request.at_wxid = at_wxid
        request.content = content
        return self.__send(request, pid)

    def send_image(self, wxid: str, image_path: str, pid: int = 0):
        warnings.warn("The function 'send_image' is deprecated, and has been replaced by the function 'send_file'",
                      DeprecationWarning)
        return self.send_file(wxid, image_path, pid)

    def send_file(self, wxid: str, file_path: str, pid: int = 0):
        """
        发送文件消息
        :param wxid: 文件消息接收wxid
        :param file_path: 文件路径
        :param pid:
        """
        if len(file_path.split("\\")) > 8:
            return self.logger.warning(f"File path is too long: {file_path}")
        request = spy_pb2.Request()
        request.cmd = SEND_FILE
        request.wxid = wxid
        request.content = file_path
        return self.__send(request, pid)

    def accept_new_contact(self, encryptusername: str, ticket: str, pid: int = 0):
        """
        接受好友请求
        :param encryptusername:
        :param ticket:
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = ACCEPT_CONTACT
        request.encryptusername = encryptusername
        request.ticket = ticket
        return self.__send(request, pid)
        
    def send_announcement(self, wxid: str, content: str, pid: int = 0):
        """
        发送群公共
        :param wxid: 群wxid
        :param content: 公告内容
        :param pid:
        :return:
        """
        if not wxid.endswith("chatroom"):
            return self.logger.warning("Can only send announcements to chatrooms")
        request = spy_pb2.Request()
        request.cmd = SEND_ANNOUNCEMENT
        request.wxid = wxid
        request.content = content
        return self.__send(request, pid)

    def create_chatroom(self, wxid: str, pid: int = 0):
        """
        创建群聊
        :param wxid: wxid,以","分隔 至少需要两个
        :param pid:
        :return:
        """
        if len(wxid.split(",")) < 2:
            return self.logger.warning("This function requires at least two wxids separated by ','")
        request = spy_pb2.Request()
        request.cmd = CREATE_CHATROOM
        request.wxid = wxid
        return self.__send(request, pid)

    def share_chatroom(self, chatroom_wxid: str, wxid: str, pid: int = 0):
        """
        分享群聊邀请链接
        :param chatroom_wxid:
        :param wxid:
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = SHARE_CHATROOM
        request.wxid = wxid
        request.chatroom_wxid = chatroom_wxid
        return self.__send(request, pid)

    def remove_chatroom_member(self, chatroom_wxid: str, wxid: str, pid: int = 0):
        """
        移除群成员
        :param chatroom_wxid:
        :param wxid:
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = REMOVE_CHATROOM_MEMBER
        request.wxid = wxid
        request.chatroom_wxid = chatroom_wxid
        return self.__send(request, pid)

    def remove_contact(self, wxid: str, pid: int = 0):
        """
        移除联系人
        :param wxid:
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = REMOVE_CONTACT
        request.wxid = wxid
        return self.__send(request, pid)

    def add_contact(self, wxid: str, chatroom_wxid: str = "", greeting: str = "", add_type: int = 1, pid: int = 0):
        """
        添加联系人
        add_type = 313: wxid、chatroom_wxid、greeting必填
        add_type = 314: wxid, greeting必填
        add_type = 315: wxid 必填
        :param wxid: 目标用户wxid
        :param chatroom_wxid: 目标用户所在群
        :param greeting: 招呼
        :param add_type: 添加类型 313:从群聊中添加 314:自己被对方删除 315:对方被自己删除
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.wxid = wxid
        if add_type == 1 and not chatroom_wxid:
            return
        request.cmd = add_type
        request.chatroom_wxid = chatroom_wxid
        request.content = greeting
        return self.__send(request, pid)

    def add_contact_from_chatroom(self, chatroom_wxid: str, wxid: str, msg: str, pid: int = 0):
        warnings.warn("The function 'add_contact_from_chatroom' is deprecated, "
                      "and has been replaced by the function 'add_contact'", DeprecationWarning)
        return self.add_contact(wxid, chatroom_wxid, msg, ADD_CONTACT_A, pid)

    def add_unidirectional_contact_a(self, wxid: str, msg: str, pid: int = 0):
        warnings.warn("The function 'add_unidirectional_contact_a' is deprecated, "
                      "and has been replaced by the function 'add_contact'", DeprecationWarning)
        return self.add_contact(wxid, "", msg, ADD_CONTACT_B, pid)

    def add_unidirectional_contact_b(self, wxid: str, pid: int = 0):
        warnings.warn("The function 'add_unidirectional_contact_b' is deprecated, "
                      "and has been replaced by the function 'add_contact'", DeprecationWarning)
        return self.add_contact(wxid, "", "", ADD_CONTACT_C, pid)

    def get_contact_status(self, wxid: str, pid: int = 0):
        """
        获取联系人状态
        :param wxid:
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = CONTACT_STATUS
        request.wxid = wxid
        return self.__send(request, pid)

    def check_contact_status(self, wxid: str, pid: int = 0):
        warnings.warn("The function 'check_contact_status' is deprecated, "
                      "and has been replaced by the function 'get_contact_status'", DeprecationWarning)
        return self.get_contact_status(wxid, pid)

    def set_chatroom_name(self, wxid: str, name: str, pid: int = 0):
        """
        设置群聊名称
        :param wxid:
        :param name:
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = SET_CHATROOM_NAME
        request.wxid = wxid
        request.content = name
        return self.__send(request, pid)

    def set_save_folder(self, folder: str, pid: int = 0):
        """
        设置保存路径
        :param folder:
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = SET_SAVE_FOLDER
        request.content = folder
        return self.__send(request, pid)

    def show_qrcode(self, output_path: str = "", pid: int = 0):
        """
        显示登录二维码
        :param output_path: 输出文件路径
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = QRCODE
        request.content = output_path
        return self.__send(request, pid)
