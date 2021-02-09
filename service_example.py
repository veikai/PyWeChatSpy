from PyWeChatSpy.service import SpyService
from flask.json import jsonify
from flask import request
from functools import wraps
from time import sleep
from PyWeChatSpy.proto import spy_pb2
from flask_cors import CORS


app = SpyService(__name__)
CORS(app, supports_credentials=True)  # 允许跨域


def verify_port(fun):
    @wraps(fun)
    def wrap(port):
        if not port and app.clients:
            port = app.clients[0]
        if port:
            return fun(port)
        else:
            return jsonify({"code": 0, "msg": "port not found"})
    return wrap


@app.route('/open_wechat')
def hello_world():
    app.spy.run(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    while True:
        if app.clients.__len__() > app.last_client_count:
            app.last_client_count = app.clients.__len__()
            return jsonify({"code": 1, "port": app.clients[-1]})
        sleep(0.5)


@app.route("/get_login_status/<int:port>")
@verify_port
def get_login_status(port):
    if status := app.client2login.get(port):
        return jsonify({"code": 1, "status": status})
    else:
        return jsonify({"code": 0, "msg": "login status not found"})


@app.route("/get_account_info/<int:port>")
@verify_port
def get_account_info(port):
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
                "phone": account_info.photo,
                "sex": account_info.sex,
                "city": account_info.city,
                "province": account_info.province,
                "country": account_info.country
            })
        sleep(0.5)
    return jsonify({"code": 0, "msg": "account info not found"})


@app.route("/send_text/<int:port>", methods=["POST"])
@verify_port
def send_text(port):
    data = request.get_json()
    wxid = data.get("wxid")
    text = data.get("text")
    at_wxid = data.get("at_wxid")
    app.spy.send_text(wxid, text, at_wxid, port)
    return jsonify({"code": 1})


if __name__ == '__main__':
    app.run()
