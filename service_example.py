from PyWeChatSpy.service import SpyService, GET_CONTACTS_LIST
from flask.json import jsonify
from flask import request
from functools import wraps
from time import sleep
from PyWeChatSpy.proto import spy_pb2
from flask_cors import CORS
import base64
import os


app = SpyService(__name__, key="18d421169d93611a5584affac335e690")
CORS(app, supports_credentials=True)  # 允许跨域


def verify_port(fun):
    @wraps(fun)
    def wrap(port):
        if not port and app.spy.port2client:
            port = list(app.spy.port2client.keys())[0]
        if port:
            return fun(port)
        else:
            return jsonify({"code": 0, "msg": "port not found"})
    return wrap


@app.route('/open_wechat')
def open_wechat():
    app.spy.run(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    i = 0
    while i < 10:
        if app.spy.port2client.keys().__len__() > app.last_client_count:
            app.last_client_count = app.spy.port2client.keys().__len__()
            return jsonify({"code": 1, "port": list(app.spy.port2client.keys())[-1]})
        i += 1
        sleep(0.5)


@app.route('/get_login_qrcode/<int:port>')
@verify_port
def get_login_qrcode(port):
    app.spy.get_login_qrcode(port)
    for i in range(20):
        if data := app.client2qrcode.get(port):
            if not data.code:
                return jsonify({"code": 0, "msg": "GET_LOGIN_QRCODE is not available"})
            app.client2qrcode.pop(port)
            qrcode_data = spy_pb2.LoginQRCode()
            qrcode_data.ParseFromString(data.bytes)
            base64_data = base64.b64encode(qrcode_data.qrcodeBytes)
            return jsonify({"code": 1, "qrcode": base64_data.decode()})
        sleep(0.5)
    return jsonify({"code": 0, "msg": "login qrcode not found"})


@app.route("/user_logout/<int:port>")
@verify_port
def user_logout(port):
    app.spy.user_logout(port)
    for i in range(20):
        if app.client2user_logout.get(port) is not None:
            code = app.client2user_logout.pop(port)
            return jsonify({"code": code})
        sleep(0.5)
    return jsonify({"code": 0})


@app.route("/close_wechat/<int:port>")
@verify_port
def close_wechat(port):
    if pid := app.client2pid.pop(port):
        os.system(f"taskkill /pid {pid}")
        app.last_client_count -= 1
        return jsonify({"code": 1})
    return jsonify({"code": 0})


@app.route("/get_login_status/<int:port>")
@verify_port
def get_login_status(port):
    if status := app.client2login.get(port):
        return jsonify({"code": 1, "status": status})
    else:
        return jsonify({"code": 0, "msg": "login status not found"})


@app.route("/get_login_info/<int:port>")
@verify_port
def get_login_info(port):
    app.spy.get_account_details(port)
    for i in range(20):
        if account_data := app.client2account.get(port):
            account_info = spy_pb2.AccountDetails()
            account_info.ParseFromString(account_data)
            return jsonify({
                "code": 1,
                "wxid": account_info.wxid,
                "nickname": account_info.nickname,
                "wechatid": account_info.wechatid,
                "autograph": account_info.autograph,
                "profile_photo_hd": account_info.profilePhotoHD,
                "profile_photo": account_info.profilePhoto,
                "phone": account_info.phone,
                "sex": account_info.sex,
                "city": account_info.city,
                "province": account_info.province,
                "country": account_info.country
            })
        sleep(0.5)
    return jsonify({"code": 0, "msg": "login info not found"})


@app.route("/send_text/<int:port>", methods=["POST"])
@verify_port
def send_text(port):
    data = request.get_json()
    wxid = data.get("wxid")
    text = data.get("text")
    at_wxid = data.get("at_wxid")
    app.spy.send_text(wxid, text, at_wxid, port)
    return jsonify({"code": 1})


@app.route("/get_contacts/<int:port>")
@verify_port
def get_contacts(port):
    app.spy.get_contacts(port)
    for i in range(20):
        if contacts_data := app.client2contacts.get(port):
            if contacts_data.type == GET_CONTACTS_LIST and not contacts_data.code:
                return jsonify({"code": 0, "msg": "GET_CONTACTS is not available"})
            contacts_list = spy_pb2.Contacts()
            contacts_list.ParseFromString(contacts_data.bytes)
            _contacts_list = []
            for contact in contacts_list.contactDetails:  # 遍历联系人列表
                _contacts_list.append({
                    "wxid": contact.wxid.str,
                    "nickname": contact.nickname.str,
                    "remark": contact.remark.str
                })
            return jsonify({"code": 1, "contacts": _contacts_list})
        sleep(0.5)
    return jsonify({"code": 0, "msg": "contacts list not found"})


if __name__ == '__main__':
    app.run()
