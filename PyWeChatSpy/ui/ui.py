from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QDesktopWidget,
    QPushButton,
    QLabel,
    QTabWidget,
    QMenu, QAction, QTextEdit, QFileDialog, QListWidget, QListWidgetItem, QCheckBox, QMainWindow, QGridLayout, QSplitter)
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import QSize, QThread, pyqtSignal, Qt, QPoint
from lxml import etree
import requests
import sys
from queue import Queue
from time import sleep
from threading import Thread
import os
import re
from PyWeChatSpy import WeChatSpy
import qdarkstyle
from PyWeChatSpy.proto.spy_pb2 import Response, AccountDetails, Contacts
from PyWeChatSpy.command import WECHAT_CONNECTED, WECHAT_LOGIN, WECHAT_LOGOUT, ACCOUNT_DETAILS, CONTACTS_LIST


my_response_queue = Queue()
key = None
if os.path.exists("key.txt"):
    with open("key.txt", "r") as rf:
        key = rf.read()
print("key:", key)
spy = WeChatSpy(response_queue=my_response_queue, key=key)
contact_filter = ("qmessage", "qqmail", "tmessage", "medianote", "floatbottle", "fmessage")
root_dir = os.path.dirname(__file__)
profile_photo_dir = os.path.join(root_dir, "profilephotos")


class MsgThread(QThread):
    signal = pyqtSignal(Response)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            msg = my_response_queue.get()
            self.signal.emit(msg)


class SendTextEdit(QTextEdit):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def keyPressEvent(self, event):
        QTextEdit.keyPressEvent(self, event)
        if event.key() == Qt.Key_Return:
            if QApplication.keyboardModifiers() == Qt.ControlModifier:
                self.append("")
            else:
                self.parent.send_msg()


class SpyUI(QMainWindow):
    def __init__(self):
        super().__init__()
        fg = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(center)
        self.resize(858, 608)
        self.move(fg.topLeft())
        self.setWindowTitle("PyWeChatSpyUI Beta 1.3.3")
        self.setWindowOpacity(0.7)  # 设置窗口透明度
        # self.layout_main = QHBoxLayout(self)
        # self.layout_left = QVBoxLayout(self)
        # self.layout_middle = QVBoxLayout(self)
        # self.layout_right = QVBoxLayout(self)
        # self.layout_main.addLayout(self.layout_left)
        # self.layout_main.addLayout(self.layout_middle)
        # self.layout_main.addLayout(self.layout_right)
        self._init_ui()
        self.main_layout.setSpacing(0)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.profile_photos = {}
        self.contacts = {}

    def _init_ui(self):
        # 主窗体
        # 创建窗口主部件
        self.main_widget = QWidget()
        # 创建主部件的网格布局
        self.main_layout = QGridLayout()
        # 设置窗口主部件布局为网格布局
        self.main_widget.setLayout(self.main_layout)
        # 创建左侧部件
        self.left_widget = QWidget()
        self.left_widget.setObjectName('left_widget')
        # 创建左侧部件的网格布局层
        self.left_layout = QGridLayout()
        # 设置左侧部件布局为网格
        self.left_widget.setLayout(self.left_layout)
        # 创建中间部件
        self.middle_widget = QWidget()
        self.middle_widget.setObjectName("middle_widget")
        self.middle_layout = QGridLayout()
        self.middle_widget.setLayout(self.middle_layout)
        # 创建右侧部件
        self.right_widget = QWidget()
        self.right_widget.setObjectName('right_widget')
        self.right_layout = QGridLayout()
        self.right_widget.setLayout(self.right_layout)

        # 左侧部件在第0行第0列，占12行1列
        self.main_layout.addWidget(self.left_widget, 0, 0, 12, 1)
        # 中间部件在第0行第6列，占12行4列
        self.main_layout.addWidget(self.middle_widget, 0, 2, 12, 4)
        # 右侧部件在第0行第6列，占12行7列
        self.main_layout.addWidget(self.right_widget, 0, 5, 12, 7)
        # 设置窗口主部件
        self.setCentralWidget(self.main_widget)
        self.single_query = QPushButton("打开微信")
        self.single_query.clicked.connect(self.open_wechat)
        self.left_layout.addWidget(self.single_query, 0, 0, 1, 1)
        # self.middle_label = QLabel("预测天气情况绘图展示区1")
        # self.middle_layout.addWidget(self.middle_label, 0, 3, 12, 4)
        self.message_TE = SendTextEdit(self)
        self.right_layout.addWidget(self.message_TE, 0, 0, 1, 7)
        # self.right_label = QLabel("预测天气情况绘图展示区2")
        # self.right_layout.addWidget(self.right_label, 0, 6, 1, 7)
        msg_thread = MsgThread()
        msg_thread.signal.connect(self.parse)
        msg_thread.start()
        self.show()

    def parse(self, data: Response):
        if data.type == WECHAT_CONNECTED:  # 微信接入
            print(f"微信客户端已接入 port:{data.port}")
            x = self.profile_photos.__len__() // 3
            y = self.profile_photos.__len__() % 3
            profile_photo_label = QLabel(self)
            default_profile_photo = QPixmap(os.path.join(profile_photo_dir, "default.png")).scaled(32, 32)
            profile_photo_label.setPixmap(default_profile_photo)
            self.profile_photos[data.port] = profile_photo_label
            self.middle_layout.addWidget(profile_photo_label, x, y, 1, 1)
        elif data.type == WECHAT_LOGIN:
            spy.get_account_details(data.port)
        elif data.type == ACCOUNT_DETAILS:
            account_details = AccountDetails()
            account_details.ParseFromString(data.bytes)
            profile_photo_url = account_details.profilePhoto
            profile_photo_path = os.path.join(profile_photo_dir, f"{account_details.wxid}.jpg")
            resp = requests.get(profile_photo_url)
            with open(profile_photo_path, "wb") as wf:
                wf.write(resp.content)
            profile_photo = QPixmap(profile_photo_path).scaled(32, 32)
            self.profile_photos[data.port].setPixmap(profile_photo)
            spy.get_contacts(data.port)
        elif data.type == CONTACTS_LIST:
            contacts = Contacts()
            contacts.ParseFromString(data.bytes)
            self.contacts[data.port] = contacts

    def open_wechat(self):
        pid = spy.run(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")

    def send_msg(self):
        content_html = self.message_TE.toHtml()
        content_html = re.sub("<span.*?>", "", content_html)
        content_html = re.sub("</span>", "", content_html)
        content_html = re.sub("<a.*?>", "", content_html)
        content_html = re.sub("</a>", "", content_html)
        content_etree = etree.HTML(content_html)
        lines = content_etree.xpath("//p")
        msg_list = []
        text_list = []
        for line in lines:
            if line.xpath("*"):
                file_path = line.xpath("img/@src")
                if file_path:
                    file_path = file_path[0]
                    if text_list:
                        msg_list.append((5, "\n".join(text_list)))
                        text_list.clear()
                    msg_list.append((6, file_path))
            text = line.xpath("text()")
            if text:
                text_list.append(text[0])
        else:
            if text_list:
                msg_list.append((5, "\n".join(text_list)))
                text_list.clear()

        def _send():
            for port, contacts in self.contacts.values():
                for contact in contacts.contactDetails:
                    if contact.wxid.str not in contact_filter:
                        for msg in msg_list:
                            if msg[0] == 5:
                                self.spy.send_text(contact.wxid.str, msg[1], port=port)
                            # elif msg[0] == 6:
                            #     self.spy.send_file(wxid, msg[1])
                            sleep(3)
        t = Thread(target=_send)
        t.daemon = True
        t.start()
        self.message_TE.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    spy_ui = SpyUI()
    sys.exit(app.exec_())