from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QDesktopWidget,
    QPushButton,
    QLabel,
    QTabWidget,
    QMenu, QAction, QTextEdit, QFileDialog, QListWidget, QListWidgetItem, QCheckBox)
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtCore import QSize, QThread, pyqtSignal, Qt, QPoint
from PyWeChatSpy import WeChatSpy
from lxml import etree
import requests
import sys
from queue import Queue
from time import sleep
from threading import Thread
import os
import re


FRIEND_LIST = []
GROUP_LIST = []
OFFICE_LIST = []
cb_contact_list = []
contact_need_details = []
current_row = 0
msg_queue = Queue()
wxid_contact = {}
contact_filter = ("qmessage", "qqmail", "tmessage", "medianote", "floatbottle", "fmessage")
key = "18d421169d93611a5584affac335e690"
if os.path.exists("key"):
    with open("key", "r") as rf:
        key = rf.read()


def parser(data: dict):
    msg_queue.put(data)


class MsgThread(QThread):
    signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            if not msg_queue.empty():
                msg = msg_queue.get()
                self.signal.emit(msg)
            else:
                sleep(0.1)


def download_image(url: str, output: str):
    resp = requests.get(url)
    if resp.status_code == 200:
        with open(output, "wb") as wf:
            wf.write(resp.content)
        return True
    return False


class ContactWidget(QWidget):
    def __init__(self, contact: dict, select_changed: classmethod):
        super().__init__()
        layout = QHBoxLayout(self)
        checkbox_contact = QCheckBox()
        checkbox_contact.__setattr__("wxid", contact["wxid"])
        checkbox_contact.setFixedSize(20, 20)
        checkbox_contact.stateChanged[int].connect(select_changed)
        cb_contact_list.append(checkbox_contact)
        layout.addWidget(checkbox_contact)
        label_profilephoto = QLabel(self)
        label_profilephoto.setFixedSize(32, 32)
        profilephoto_path = "profilephotos/default.jpg"
        if os.path.exists(f"profilephotos/{contact['wxid']}.jpg"):
            profilephoto_path = f"profilephotos/{contact['wxid']}.jpg"
        default_profilephoto = QPixmap(profilephoto_path).scaled(32, 32)
        label_profilephoto.setPixmap(default_profilephoto)
        layout.addWidget(label_profilephoto)
        label_nickname = QLabel(self)
        nickname = contact["nickname"]
        if remark := contact.get("remark"):
            nickname = f"{nickname}({remark})"
        if count := contact.get("member_count"):
            nickname = f"{nickname}[{count}]"
        label_nickname.setText(nickname)
        layout.addWidget(label_nickname)


class ContactSearchWidget(QWidget):
    def __init__(self, contact: dict):
        super().__init__()
        layout = QHBoxLayout(self)
        label_profilephoto = QLabel(self)
        label_profilephoto.setFixedSize(32, 32)
        profilephoto_path = "profilephotos/default.jpg"
        if os.path.exists(f"profilephotos/{contact['wxid']}.jpg"):
            profilephoto_path = f"profilephotos/{contact['wxid']}.jpg"
        default_profilephoto = QPixmap(profilephoto_path).scaled(32, 32)
        label_profilephoto.setPixmap(default_profilephoto)
        layout.addWidget(label_profilephoto)
        label_nickname = QLabel(self)
        nickname = contact["nickname"]
        if remark := contact.get("remark"):
            nickname = f"{nickname}({remark})"
        if count := contact.get("member_count"):
            nickname = f"{nickname}[{count}]"
        label_nickname.setText(nickname)
        layout.addWidget(label_nickname)


class MessageWidget(QWidget):
    def __init__(self, message: dict):
        super().__init__()
        layout_main = QHBoxLayout(self)
        layout_side = QVBoxLayout(self)
        label_content = QLabel(self)
        label_content.setWordWrap(True)
        label_content.adjustSize()
        label_content.setFixedWidth(300)
        label_speaker = QLabel(self)
        if message["self"]:
            layout_main.setAlignment(Qt.AlignRight)
            label_content.setAlignment(Qt.AlignRight)
            label_speaker.setAlignment(Qt.AlignRight)
        else:
            layout_main.setAlignment(Qt.AlignLeft)
            label_content.setAlignment(Qt.AlignLeft)
            label_speaker.setAlignment(Qt.AlignLeft)
        label_profilephoto = QLabel(self)
        label_profilephoto.setFixedSize(32, 32)
        profilephoto_path = "profilephotos/default.jpg"
        if os.path.exists(f"profilephotos/{message['wxid1']}.jpg"):
            profilephoto_path = f"profilephotos/{message['wxid1']}.jpg"
        default_profilephoto = QPixmap(profilephoto_path).scaled(32, 32)
        label_profilephoto.setPixmap(default_profilephoto)
        speaker = ""
        wxid1 = message["wxid1"]
        if contact := wxid_contact.get(wxid1):
            speaker = contact["nickname"]
            if remark := contact.get("remark"):
                speaker = f"{speaker}({remark})"
        label_speaker.setText(speaker)
        layout_side.addWidget(label_speaker)
        if message["msg_type"] == 1:
            label_content.setText(message["content"])
        elif message["msg_type"] == 3:
            label_content.setText("图片消息，请在手机上查看")
        elif message["msg_type"] == 43:
            if message.get("content"):
                label_content.setText("不支持的消息类型，请在手机上查看")
            else:
                label_content.setText("视频消息，请在手机上查看")
        elif message["msg_type"] == 47:
            label_content.setText("表情包消息，请在手机上查看")
        elif message["msg_type"] == 49:
            label_content.setText("小程序或其他分享消息，请在手机上查看")
        else:
            label_content.setText("不支持的消息类型，请在手机上查看")
        layout_side.addWidget(label_content)
        if message["self"]:
            layout_main.addLayout(layout_side)
            layout_main.addWidget(label_profilephoto)
        else:
            layout_main.addWidget(label_profilephoto)
            layout_main.addLayout(layout_side)


class SettingWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("设置")
        self.parent = parent
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.West)
        self.tab_widget.setFixedSize(300, 200)
        self.tab_common = QListWidget(self)
        self.tab_widget.addTab(self.tab_common, "通用")
        item = QListWidgetItem()
        item.setSizeHint(QSize(200, 50))
        self.cb_auto_accept = QCheckBox("自动通过好友请求")
        self.tab_common.addItem(item)
        self.tab_common.setItemWidget(item, self.cb_auto_accept)


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


class SpyUI(QWidget):
    def __init__(self):
        super().__init__()
        self.layout_main = QHBoxLayout(self)
        self.setting_widget = SettingWidget(self)
        self.wxid = ""
        self.init_ui()

    def init_ui(self):
        fg = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(center)
        # 设置窗体
        self.setting_widget.resize(300, 200)
        self.setting_widget.move(fg.topLeft())
        self.setting_widget.hide()
        # 主窗体
        self.resize(858, 608)
        self.move(fg.topLeft())
        self.setWindowTitle("PyWeChatSpyUI Beta 1.3.3")
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    spy = SpyUI()
    sys.exit(app.exec_())
