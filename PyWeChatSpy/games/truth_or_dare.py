from functools import wraps
from ..command import CHAT_MESSAGE, CONTACT_DETAILS
from ..proto import spy_pb2
from ..spy import WeChatSpy
from lxml import etree


class TruthOrDare:
    def __init__(self, spy: WeChatSpy):
        self.spy = spy
        self.admin = None
        self.group = None
        self.group_member = dict()
        self.count = 0
        self.records = []
        self.record = dict()
        self.ask = []
        self.answer = []

    def game(self, func):
        @wraps(func)
        def wrapper(data):
            if data.type == CHAT_MESSAGE:
                chat_message = spy_pb2.ChatMessage()
                chat_message.ParseFromString(data.bytes)
                for message in chat_message.message:
                    _type = message.type  # 消息类型 1.文本|3.图片...自行探索
                    _from = message.wxidFrom.str  # 消息发送方
                    _to = message.wxidTo.str  # 消息接收方
                    # if _to == "filehelper":
                    #     print(message)
                    content = message.content.str  # 消息内容
                    _from_group_member = ""
                    if _from.endswith("@chatroom"):  # 群聊消息
                        _from_group_member = message.content.str.split(':\n', 1)[0]  # 群内发言人
                        content = message.content.str.split(':\n', 1)[-1]  # 群聊消息内容
                    if _type == 1:  # 文本消息
                        if not self.group and content == "真心话大冒险":
                            self.admin = _from_group_member
                            if _from_group_member == "":
                                self.group = _to
                            else:
                                self.group = _from
                            self.spy.get_contact_details(self.group)
                        elif self.admin == _from_group_member:
                            if content == "开始":
                                self.count += 1
                                self.record.clear()
                                self.ask.clear()
                                self.answer.clear()
                                self.spy.send_text(self.group, f"第{self.count}轮游戏开始,请掷骰子")
                            elif content == "结算":
                                values = self.record.values()
                                _max = max(values)
                                _min = min(values)
                                for k, v in self.record.items():
                                    if v == _max:
                                        self.ask.append(k)
                                    elif v == _min:
                                        self.answer.append(k)
                                ask = answer = ""
                                for w in self.ask:
                                    ask += f"{self.group_member[w]} "
                                # w_ask = ",".join(self.ask)
                                for w in self.answer:
                                    answer = f"{self.group_member[w]} "
                                # w_answer = ",".join(self.answer)
                                message = f"第{self.count}轮游戏结算,请{ask}向{answer}提问"
                                self.spy.send_text(self.group, message)
                    elif _type == 47:
                        if _from == self.group or _to == self.group:
                            xml = etree.XML(content)
                            game_type = xml.xpath("/msg/gameext/@type")[0]
                            if game_type == "2":  # 骰子游戏
                                fromusername = xml.xpath("/msg/emoji/@fromusername")[0]
                                value = int(xml.xpath("/msg/gameext/@content")[0]) - 3
                                if not self.record.get(fromusername):
                                    self.record[fromusername] = value
            elif data.type == CONTACT_DETAILS:
                contact_details_list = spy_pb2.Contacts()
                contact_details_list.ParseFromString(data.bytes)
                for contact_details in contact_details_list.contactDetails:  # 遍历联系人详情
                    wxid = contact_details.wxid.str  # 联系人wxid
                    if wxid == self.group:
                        # nickname = contact_details.nickname.str  # 联系人昵称
                        # remark = contact_details.remark.str  # 联系人备注
                        group_member_list = contact_details.groupMemberList  # 群成员列表
                        member_count = group_member_list.memberCount  # 群成员数量
                        for group_member in group_member_list.groupMember:  # 遍历群成员
                            member_wxid = group_member.wxid  # 群成员wxid
                            member_nickname = group_member.nickname  # 群成员昵称
                            self.group_member[member_wxid] = member_nickname
                        self.spy.send_text(
                            self.group, f"游戏成员[{member_count}]加载完成,游戏准备就绪,请管理员发送'开始'开始游戏，发送'结算'结算此轮游戏")
            func(data)
        return wrapper

