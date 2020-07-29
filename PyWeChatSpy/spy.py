import os
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from time import sleep
from subprocess import Popen, PIPE
from .exceptions import handle_error_code, ParserError
import logging
import warnings
from uuid import uuid4
from .proto import spy_pb2
from queue import Queue


class WeChatSpy:
    def __init__(
            self, parser=None, error_handle=None, multi: bool = False, key: str = None, logger: logging.Logger = None):
        self.__byte_queue = Queue()
        self.client_list = []
        # TODO: 异常处理函数
        self.__error_handle = error_handle
        # 是否多开微信PC客户端
        self.__multi = multi
        self.__mutex = Lock()
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
            raise ParserError()
        self.pid_list = []
        self.__pid2client = {}
        self.__socket_server = socket(AF_INET, SOCK_STREAM)
        self.__socket_server.bind(("127.0.0.1", 9527))
        self.__socket_server.listen(1)
        t_start_server = Thread(target=self.__start_server)
        t_start_server.daemon = True
        t_start_server.name = "socket accept"
        t_start_server.start()
        t_parse = Thread(target=self.__parse)
        t_parse.daemon = True
        t_parse.name = "parser"
        t_parse.start()

    def __start_server(self):
        while True:
            socket_client, client_address = self.__socket_server.accept()
            if socket_client not in self.client_list:
                self.client_list.append(socket_client)
                while len(self.client_list) != len(self.pid_list):
                    sleep(1)
                self.__pid2client[self.pid_list[-1]] = socket_client
                self.logger.info(f"A WeChat process successfully connected (PID:{self.pid_list[-1]})")
            if self.__key:
                request = spy_pb2.Request()
                request.cmd = 9527
                request.key = self.__key
                request.uuid = ""
                request.sync = 0
                data = request.SerializeToString()
                data_length_bytes = int.to_bytes(len(data), length=4, byteorder="little")
                socket_client.send(data_length_bytes + data)
            t_socket_client_receive = Thread(target=self.receive, args=(socket_client, ))
            t_socket_client_receive.name = f"client {client_address[1]}"
            t_socket_client_receive.daemon = True
            t_socket_client_receive.start()

    def receive(self, socket_client: socket):
        while True:
            try:
                _bytes = socket_client.recv(4096)
                self.__mutex.acquire()
                for _byte in _bytes:
                    self.__byte_queue.put(int.to_bytes(_byte, 1, "little"))
                self.__mutex.release()
            except Exception as e:
                for pid, client in self.__pid2client.items():
                    if client == socket_client:
                        self.__pid2client.pop(pid)
                        return self.logger.warning(f"A WeChat process has disconnected (PID:{pid}) : {e}")
                else:
                    pid = "unknown"
                    return self.logger.warning(f"A WeChat process has disconnected (PID:{pid}) : {e}")

    def __send(self, request: spy_pb2.Request, pid: int):
        for i in range(5):
            if not pid and self.pid_list:
                pid = self.pid_list[0]
            socket_client = self.__pid2client.get(pid)
            if socket_client:
                uuid = uuid4().__str__()
                request.uuid = uuid
                request.sync = 0
                data = request.SerializeToString()
                data_length_bytes = int.to_bytes(len(data), length=4, byteorder="little")
                try:
                    socket_client.send(data_length_bytes + data)
                except Exception as e:
                    for pid, v in self.__pid2client.items():
                        if v == socket_client:
                            self.__pid2client.pop(pid)
                            return self.logger.warning(f"A WeChat process has disconnected (PID:{pid}) : {e}")
                    else:
                        pid = "unknown"
                        return self.logger.warning(f"A WeChat process has disconnected (PID:{pid}) : {e}")
                break
            else:
                sleep(1)
        else:
            return self.logger.error(f"Send Timeout: Socket connection not found")

    def run(self, background: bool = False):
        current_path = os.path.split(os.path.abspath(__file__))[0]
        launcher_path = os.path.join(current_path, "Launcher.exe")
        cmd_str = f"{launcher_path} multi" if self.__multi else launcher_path
        p = Popen(cmd_str, shell=True, stdout=PIPE)
        res_code, err = p.communicate()
        res_code = res_code.decode()
        handle_error_code(res_code)
        res_code = int(res_code)
        self.pid_list.append(res_code)
        if not background:
            while True:
                sleep(86400)

    def __parse(self):
        while True:
            if self.__byte_queue.empty():
                sleep(0.1)
                continue
            self.__mutex.acquire()
            byte = b""
            for i in range(4):
                byte += self.__byte_queue.get()
            length = int.from_bytes(byte, "little")
            byte = b""
            for i in range(length):
                byte += self.__byte_queue.get()
            response = spy_pb2.Response()
            response.ParseFromString(byte)
            t = Thread(target=self.__parser, args=(response, ))
            t.daemon = True
            t.start()
            self.__mutex.release()

    def query_login_info(self, pid: int = 0):
        """
        查询当前登录信息
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = 301
        return self.__send(request, pid)

    def query_contact_details(self, wxid: str, update: bool = False, pid: int = 0):
        """
        查询联系人详情
        :param wxid: 联系人wxid
        :param update: 是否更新最新详情(需请求微信服务器 速度较慢)
        :param pid:
        """
        data = {"code": 2, "wxid": wxid, "update": update}
        return self.__send(data, pid)

    def query_contact_list(self, pid: int = 0):
        """
        查询联系人详情
        :param pid:
        :return:
        """
        request = spy_pb2.Request()
        request.cmd = 302
        return self.__send(request, pid)

    def query_chatroom_member(self, wxid: str, pid: int = 0):
        """
        查询群成员列表
        :param wxid: 群wxid
        :param pid:
        :return:
        """
        data = {"code": 4, "wxid": wxid}
        return self.__send(data, pid)

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
        data = {"code": 5, "wxid": wxid, "at_wxid": at_wxid, "content": content}
        return self.__send(data, pid)

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
        data = {"code": 6, "wxid": wxid, "file_path": file_path}
        return self.__send(data, pid)

    def accept_new_contact(self, encryptusername: str, ticket: str, pid: int = 0):
        """
        接受好友请求
        :param encryptusername:
        :param ticket:
        :param pid:
        :return:
        """
        data = {"code": 7, "encryptusername": encryptusername, "ticket": ticket}
        return self.__send(data, pid)
        
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
        data = {"code": 8, "wxid": wxid, "content": content}
        return self.__send(data, pid)

    def create_chatroom(self, wxid: str, pid: int = 0):
        """
        创建群聊
        :param wxid: wxid,以","分隔 至少需要两个
        :param pid:
        :return:
        """
        if len(wxid.split(",")) < 2:
            return self.logger.warning("This function requires at least two wxids separated by ','")
        data = {"code": 9, "wxid": wxid}
        return self.__send(data, pid)

    def share_chatroom(self, chatroom_wxid: str, wxid: str, pid: int = 0):
        """
        分享群聊邀请链接
        :param chatroom_wxid:
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 10, "wxid": wxid, "chatroom_wxid": chatroom_wxid}
        return self.__send(data, pid)

    def remove_chatroom_member(self, chatroom_wxid: str, wxid: str, pid: int = 0):
        """
        移除群成员
        :param chatroom_wxid:
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 11, "wxid": wxid, "chatroom_wxid": chatroom_wxid}
        return self.__send(data, pid)

    def remove_contact(self, wxid: str, pid: int = 0):
        """
        移除联系人
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 12, "wxid": wxid}
        return self.__send(data, pid)

    def add_contact_from_chatroom(self, chatroom_wxid: str, wxid: str, msg: str, pid: int = 0):
        """
        将群成员添加为好友
        :param chatroom_wxid: 群wxid
        :param wxid: 群成员wxid
        :param msg: 好友申请信息
        :param pid:
        :return:
        """
        data = {"code": 13, "wxid": wxid, "chatroom_wxid": chatroom_wxid, "msg": msg}
        return self.__send(data, pid)

    def add_unidirectional_contact_a(self, wxid: str, msg: str, pid: int = 0):
        """
        添加单向好友(自己被对方删除)
        :param wxid:
        :param msg: 好友申请信息
        :param pid:
        :return:
        """
        data = {"code": 14, "wxid": wxid, "msg": msg}
        return self.__send(data, pid)

    def add_unidirectional_contact_b(self, wxid: str, pid: int = 0):
        """
        添加单向好友(对方被自己删除)
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 15, "wxid": wxid}
        return self.__send(data, pid)

    def check_contact_status(self, wxid: str, pid: int = 0):
        """
        检查联系人状态
        :param wxid:
        :param pid:
        :return:
        """
        data = {"code": 16, "wxid": wxid}
        return self.__send(data, pid)

    def set_chatroom_name(self, wxid: str, name: str, pid: int = 0):
        """
        设置群聊名称
        :param wxid:
        :param name:
        :param pid:
        :return:
        """
        data = {"code": 17, "wxid": wxid, "name": name}
        return self.__send(data, pid)

    def set_save_folder(self, folder: str, pid: int = 0):
        """
        设置保存路径
        :param folder:
        :param pid:
        :return:
        """
        data = {"code": 18, "folder": folder}
        return self.__send(data, pid)

    def show_qrcode(self, output_path: str = "", pid: int = 0):
        """
        显示登录二维码
        :param output_path: 输出文件路径
        :param pid:
        :return:
        """
        data = {"code": 19, "output_path": output_path}
        return self.__send(data, pid)
