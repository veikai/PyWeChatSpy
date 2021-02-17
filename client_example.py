import requests
import base64

# resp = requests.get("http://localhost:5000/open_wechat").json()
# print(resp)
# input()  # 等待手动登录
# resp = requests.get("http://localhost:5000/get_login_qrcode/0").json()
# print(resp)
# if resp["code"]:
#     with open("qrcode.png", "wb") as wf:
#         wf.write(base64.b64decode(resp["qrcode"]))
# requests.post("http://localhost:5000/send_text/0", json={"wxid": "filehelper", "text": "Hello SpyService"})