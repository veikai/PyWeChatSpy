import requests
import base64


resp = requests.get("http://localhost:5000/open_wechat").json()
print(resp)
input()  # 等待手动登录
resp = requests.get(f"http://localhost:5000/get_login_qrcode/{resp['port']}").json()
print(resp)
with open("qrcode.png", "wb") as wf:
    wf.write(base64.b64decode(resp["qrcode"]))
input()
resp = requests.get("http://localhost:5000/user_logout/0").json()
print(resp)
input()
resp = requests.get("http://localhost:5000/close_wechat/0").json()
print(resp)


def a():
    print(111)
    yield
    print(222)
    yield


def b():
    print(333)
    yield
    print(444)
    yield

c = a()
d = b()
next(c)
next(d)
next(c)
next(d)