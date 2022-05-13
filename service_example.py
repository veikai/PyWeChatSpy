from PyWeChatSpy.service import SpyService, GET_CONTACTS_LIST, GET_LOGIN_QRCODE, GET_CONTACT_DETAILS
from flask.json import jsonify
from flask import request, send_from_directory
from functools import wraps
from time import sleep
from PyWeChatSpy.proto import spy_pb2
from flask_cors import CORS
from uuid import uuid4
import base64
import os


app = SpyService(__name__, key="18d421169d93611a5584affac335e690")
app.config['UPLOAD_FOLDER'] = r"D:\cache"
WECHAT_PROFILE = r"C:\Users\administrator\Documents\WeChat Files"
CORS(app, supports_credentials=True)  # 允许跨域


def verify_port(fun):
    @wraps(fun)
    def wrap(port):
        if not port and app.spy.port2client:
            port = list(app.spy.port2client.keys())[0]
        if port:
            _id = uuid4().__str__()
            return fun(port, _id)
        else:
            return jsonify({"code": 0, "msg": "port not found"})
    return wrap


def verify_json(*args):
    def decorator(fun):
        @wraps(fun)
        def wrap(port, _id):
            if not request.json:
                return jsonify({"code": 0, "msg": "json error"})
            for param in args:
                if not request.json.get(param):
                    return jsonify({"code": 0, "msg": "parameters error"})
            return fun(port, _id)
        return wrap
    return decorator


@app.route('/open_wechat')
def open_wechat():
    app.spy.run(r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe")
    i = 0
    while i < 20:
        if app.spy.port2client.keys().__len__() > app.last_client_count:
            app.last_client_count = app.spy.port2client.keys().__len__()
            return jsonify({"code": 1, "port": list(app.spy.port2client.keys())[-1]})
        i += 1
        sleep(0.5)
    return jsonify({"code": 0, "msg": "wechat not found"})


@app.route('/get_login_qrcode/<int:port>')
@verify_port
def get_login_qrcode(port, _id):
    app.spy.get_login_qrcode(port, _id)
    for i in range(20):
        if app.client2response.get(_id):
            data = app.client2response.pop(_id)
            if data.type == GET_LOGIN_QRCODE and not data.code:
                return jsonify({"code": 0, "msg": "GET_LOGIN_QRCODE is not available"})
            qrcode_data = spy_pb2.LoginQRCode()
            qrcode_data.ParseFromString(data.bytes)
            base64_data = base64.b64encode(qrcode_data.qrcodeBytes)
            return jsonify({"code": 1, "qrcode": base64_data.decode()})
        sleep(0.5)
    return jsonify({"code": 0, "msg": "login qrcode not found"})


@app.route("/user_logout/<int:port>")
@verify_port
def user_logout(port, _id):
    app.spy.user_logout(port, _id)
    for i in range(20):
        if app.client2user_logout.get(port) is not None:
            code = app.client2user_logout.pop(port)
            return jsonify({"code": code})
        sleep(0.5)
    return jsonify({"code": 0})


@app.route("/close_wechat/<int:port>")
@verify_port
def close_wechat(port, _id):
    if pid := app.client2pid.get(port):
        app.client2pid.pop(port)
        os.system(f"taskkill /pid {pid}")
        app.last_client_count -= 1
        return jsonify({"code": 1})
    return jsonify({"code": 0})


if __name__ == '__main__':
    app.run()
