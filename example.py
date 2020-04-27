from PyWeChatSpy import WeChatSpy
import requests


contact_dict = {}


def get_reply(data):
    url = f"http://api.douqq.com/?key=&msg={data}"  # key获取地址http://xiao.douqq.com/
    resp = requests.get(url)
    return resp.text


def parser(data):
    if data["type"] == 1:
        # 登录信息
        spy.logger.info(data)
    elif data["type"] == 203:
        # 微信登出
        spy.logger.info("微信退出登录")
    elif data["type"] == 5:
        # 消息
        for item in data["data"]:
            spy.logger.info(item)
            wxid1, wxid2 = item["wxid1"], item.get("wxid2")
            if item["msg_type"] == 1:
                reply = get_reply(item["content"])
                spy.send_text(wxid1, reply)
            if contact := contact_dict.get(wxid1):
                spy.logger.info(contact)
            else:
                spy.query_contact_details(wxid1)
            if wxid1.endswith("chatroom") and wxid2:
                if contact := contact_dict.get(wxid2):
                    spy.logger.info(contact)
                else:
                    spy.query_contact_details(wxid2, wxid1)
    elif data["type"] == 2:
        # 联系人信息
        spy.logger.info(data)


if __name__ == '__main__':
    spy = WeChatSpy(parser=parser)
    spy.add_log_output_file()  # 添加日志输出文件
    spy.run()
