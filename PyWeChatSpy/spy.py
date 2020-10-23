import os
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from .exceptions import ParserError
import logging
import warnings
from uuid import uuid4
from .proto import spy_pb2
from .command import *
from ctypes import cdll, c_char_p


class WeChatSpy:
    def __init__(self, parser=None, key: str = None, logger: logging.Logger = None):
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
            self.__parser = parser
        else:
            raise ParserError("Parser must be callable")
        self.__port2client = dict()
        self.__pid2port = dict()
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
        helper_path = os.path.join(current_path, "SpyHelper.exe")
        attach_thread = Thread(target=os.system, args=(helper_path,))
        attach_thread.daemon = True
        attach_thread.name = "attach"
        attach_thread.start()

    def __start_server(self):
        while True:
            socket_client, client_address = self.__socket_server.accept()
            self.__port2client[client_address[1]] = socket_client
            self.logger.info(f"A WeChat process from {client_address} successfully connected")
            if self.__key:
                self.set_commercial(self.__key, port=client_address[1])
            t_socket_client_receive = Thread(target=self.receive, args=(socket_client, client_address))
            t_socket_client_receive.name = f"wechat {client_address}"
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
                    response.port = client_address[1]
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
                        if response.type == WECHAT_CONNECTED:
                            self.__pid2port[response.pid] = client_address[1]
                        t = Thread(target=self.__parser, args=(response,))
                        t.name = f"wechat {client_address}"
                        t.daemon = True
                        t.start()
                else:
                    break

    def __send(self, request: spy_pb2.Request, pid: int = 0, port: int = 0):
        if pid:
            self.logger.warning(
                "We recommend using the parameter 'port' to distinguish between multiple different WeChat clients.")
            if not (port := self.__pid2port.get(pid)):
                self.logger.error(f"Failure to find port by pid:{pid}")
                return False
        if not port and self.__port2client:
            socket_client = list(self.__port2client.values())[0]
        elif not (socket_client := self.__port2client.get(port)):
            self.logger.error(f"Failure to find socket client by port:{port}")
            return False
        request.uuid = uuid4().__str__()
        data = request.SerializeToString()
        data_length_bytes = int.to_bytes(len(data), length=4, byteorder="little")
        try:
            socket_client.send(data_length_bytes + data)
            return True
        except Exception as e:
            self.logger.warning(f"The WeChat process {port} has disconnected: {e}")
            return False

    def run(self, wechat: str, bit: int = 64):
        current_path = os.path.split(os.path.abspath(__file__))[0]
        if bit == 64:
            dll_path = os.path.join(current_path, "SpyHelper_x64.dll")
        else:
            dll_path = os.path.join(current_path, "SpyHelper_x86.dll")
        try:
            dll = cdll.LoadLibrary(dll_path)
        except FileNotFoundError:
            self.logger.error("OpenHelper not found")
            return 0
        except OSError as e:
            if e.errno == 8:
                return self.run(wechat, 64) if bit != 64 else self.run(wechat, 32)
            self.logger.error(e)
            return 0
        pid = dll.OpenWeChat(c_char_p(wechat.encode()))
        return pid

    def set_commercial(self, key: str, pid: int = 0, port: int = 0):
        request = spy_pb2.Request()
        request.cmd = SYSTEM
        request.content = key
        request.uuid = ""
        self.__send(request, pid, port)

    def get_login_info(self, pid: int = 0, port: int = 0):
        """
        获取当前登录信息
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = LOGIN_INFO
        return self.__send(request, pid, port)

    def query_login_info(self, pid: int = 0, port: int = 0):
        warnings.warn(
            "The function 'query_login_info' is deprecated, and has been replaced by the function 'get_login_info'",
            DeprecationWarning)
        return self.get_login_info(pid, port)

    def get_contacts(self, pid: int = 0, port: int = 0):
        """
        获取联系人详情
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = CONTACTS
        return self.__send(request, pid, port)

    def query_contact_list(self, pid: int = 0, port: int = 0):
        warnings.warn(
            "The function 'query_contact_list' is deprecated, and has been replaced by the function 'get_contact_list'",
            DeprecationWarning)
        return self.get_contacts(pid, port)

    def get_contact_details(self, wxid: str, update: bool = False, pid: int = 0, port: int = 0):
        """
        获取联系人详情
        :param wxid: 联系人wxid
        :param update: 是否更新最新详情(需请求微信服务器 速度较慢)
        :param pid:
        :param port:
        """
        request = spy_pb2.Request()
        request.cmd = CONTACT_DETAILS
        request.wxid = wxid
        request.update = 1 if update else 0
        return self.__send(request, pid, port)

    def query_contact_details(self, wxid: str, update: bool = False, pid: int = 0, port: int = 0):
        warnings.warn(
            "The function 'query_contact_details' is deprecated, "
            "and has been replaced by the function 'get_contact_details'", DeprecationWarning)
        return self.get_contact_details(wxid, update, pid, port)

    def get_chatroom_members(self, wxid: str, pid: int = 0, port: int = 0):
        """
        获取群成员列表
        :param wxid: 群wxid
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = CHATROOM_MEMBERS
        request.wxid = wxid
        return self.__send(request, pid, port)

    def query_chatroom_member(self, wxid: str, pid: int = 0, port: int = 0):
        warnings.warn(
            "The function 'query_chatroom_member' is deprecated, "
            "and has been replaced by the function 'get_chatroom_members'", DeprecationWarning)
        return self.get_chatroom_members(wxid, pid, port)

    def send_text(self, wxid: str, content: str, at_wxid: str = "", pid: int = 0, port: int = 0):
        """
        发送文本消息
        :param wxid: 文本消息接收wxid
        :param content: 文本消息内容
        :param at_wxid: 如果wxid为群wxid且需要@群成员 此参数为被@群成员wxid，以英文逗号分隔
        :param pid:
        :param port:
        """
        if not wxid.endswith("chatroom"):
            at_wxid = ""
        request = spy_pb2.Request()
        request.cmd = SEND_TEXT
        request.wxid = wxid
        request.at_wxid = at_wxid
        request.content = content
        return self.__send(request, pid, port)

    def send_image(self, wxid: str, image_path: str, pid: int = 0, port: int = 0):
        warnings.warn("The function 'send_image' is deprecated, and has been replaced by the function 'send_file'",
                      DeprecationWarning)
        return self.send_file(wxid, image_path, pid, port)

    def send_file(self, wxid: str, file_path: str, pid: int = 0, port: int = 0):
        """
        发送文件消息
        :param wxid: 文件消息接收wxid
        :param file_path: 文件路径
        :param pid:
        :param port:
        """
        if len(file_path.split("\\")) > 8:
            return self.logger.warning(f"File path is too long: {file_path}")
        request = spy_pb2.Request()
        request.cmd = SEND_FILE
        request.wxid = wxid
        request.content = file_path
        return self.__send(request, pid, port)

    def accept_new_contact(self, encryptusername: str, ticket: str, pid: int = 0, port: int = 0):
        """
        接受好友请求
        :param encryptusername:
        :param ticket:
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = ACCEPT_CONTACT
        request.encryptusername = encryptusername
        request.ticket = ticket
        return self.__send(request, pid, port)

    def send_announcement(self, wxid: str, content: str, pid: int = 0, port: int = 0):
        """
        发送群公共
        :param wxid: 群wxid
        :param content: 公告内容
        :param pid:
        :param port:
        :return:
        """
        if not wxid.endswith("chatroom"):
            return self.logger.warning("Can only send announcements to chatrooms")
        request = spy_pb2.Request()
        request.cmd = SEND_ANNOUNCEMENT
        request.wxid = wxid
        request.content = content
        return self.__send(request, pid, port)

    def create_chatroom(self, wxid: str, pid: int = 0, port: int = 0):
        """
        创建群聊
        :param wxid: wxid,以","分隔 至少需要两个
        :param pid:
        :param port:
        :return:
        """
        if len(wxid.split(",")) < 2:
            return self.logger.warning("This function requires at least two wxids separated by ','")
        request = spy_pb2.Request()
        request.cmd = CREATE_CHATROOM
        request.wxid = wxid
        return self.__send(request, pid, port)

    def share_chatroom(self, chatroom_wxid: str, wxid: str, pid: int = 0, port: int = 0):
        """
        分享群聊邀请链接
        :param chatroom_wxid:
        :param wxid:
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = SHARE_CHATROOM
        request.wxid = wxid
        request.chatroom_wxid = chatroom_wxid
        return self.__send(request, pid, port)

    def remove_chatroom_member(self, chatroom_wxid: str, wxid: str, pid: int = 0, port: int = 0):
        """
        移除群成员
        :param chatroom_wxid:
        :param wxid:
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = REMOVE_CHATROOM_MEMBER
        request.wxid = wxid
        request.chatroom_wxid = chatroom_wxid
        return self.__send(request, pid, port)

    def remove_contact(self, wxid: str, pid: int = 0, port: int = 0):
        """
        移除联系人
        :param wxid:
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = REMOVE_CONTACT
        request.wxid = wxid
        return self.__send(request, pid, port)

    def add_contact(self, wxid: str, chatroom_wxid: str = "", greeting: str = "",
                    add_type: int = 1, pid: int = 0, port: int = 0):
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
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.wxid = wxid
        if add_type == 1 and not chatroom_wxid:
            return
        request.cmd = add_type
        request.chatroom_wxid = chatroom_wxid
        request.content = greeting
        return self.__send(request, pid, port)

    def add_contact_from_chatroom(self, chatroom_wxid: str, wxid: str, msg: str, pid: int = 0, port: int = 0):
        warnings.warn("The function 'add_contact_from_chatroom' is deprecated, "
                      "and has been replaced by the function 'add_contact'", DeprecationWarning)
        return self.add_contact(wxid, chatroom_wxid, msg, ADD_CONTACT_A, pid, port)

    def add_unidirectional_contact_a(self, wxid: str, msg: str, pid: int = 0, port: int = 0):
        warnings.warn("The function 'add_unidirectional_contact_a' is deprecated, "
                      "and has been replaced by the function 'add_contact'", DeprecationWarning)
        return self.add_contact(wxid, "", msg, ADD_CONTACT_B, pid, port)

    def add_unidirectional_contact_b(self, wxid: str, pid: int = 0, port: int = 0):
        warnings.warn("The function 'add_unidirectional_contact_b' is deprecated, "
                      "and has been replaced by the function 'add_contact'", DeprecationWarning)
        return self.add_contact(wxid, "", "", ADD_CONTACT_C, pid, port)

    def get_contact_status(self, wxid: str, pid: int = 0, port: int = 0):
        """
        获取联系人状态
        :param wxid:
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = CONTACT_STATUS
        request.wxid = wxid
        return self.__send(request, pid, port)

    def check_contact_status(self, wxid: str, pid: int = 0, port: int = 0):
        warnings.warn("The function 'check_contact_status' is deprecated, "
                      "and has been replaced by the function 'get_contact_status'", DeprecationWarning)
        return self.get_contact_status(wxid, pid, port)

    def set_chatroom_name(self, wxid: str, name: str, pid: int = 0, port: int = 0):
        """
        设置群聊名称
        :param wxid:
        :param name:
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = SET_CHATROOM_NAME
        request.wxid = wxid
        request.content = name
        return self.__send(request, pid, port)

    def set_save_folder(self, folder: str, pid: int = 0, port: int = 0):
        """
        设置保存路径
        :param folder:
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = SET_SAVE_FOLDER
        request.content = folder
        return self.__send(request, pid, port)

    def show_qrcode(self, output_path: str = "", pid: int = 0, port: int = 0):
        """
        显示登录二维码
        :param output_path: 输出文件路径
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = QRCODE
        request.content = output_path
        return self.__send(request, pid, port)

    def set_remark(self, wxid: str, remark: str, pid: int = 0, port: int = 0):
        """
        设置联系人备注
        :param wxid: 需要设置备注的联系人的wxid
        :param remark: 备注内容
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = SET_REMARK
        request.wxid = wxid
        request.content = remark
        return self.__send(request, pid, port)

    def get_chatroom_invite_url(self, wxid: str, url: str, pid: int = 0, port: int = 0):
        """
        获取群邀请链接
        :param wxid: 发送群邀请链接的人的wxid
        :param url: 群邀请解析出来的url
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = GET_CHATROOM_INVITATION_URL
        request.wxid = wxid
        request.content = url
        return self.__send(request, pid, port)

    def send_link_card(
            self, receive_wxid: str, send_wxid: str, content: str, image_path: str, pid: int = 0, port: int = 0):
        """
        发送链接卡片
        :param receive_wxid:
        :param send_wxid:
        :param content:
        :param image_path:
        :param pid:
        :param port:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = SEND_LINK_CARD
        request.wxid = receive_wxid
        request.content = content
        request.at_wxid = send_wxid
        request.ticket = image_path
        return self.__send(request, pid, port)
