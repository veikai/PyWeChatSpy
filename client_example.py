import requests
import base64
import time
import os


i = 0
a = time.time()
resp = requests.get("http://localhost:5000/open_wechat").json()
print(i, resp, time.time() - a)
port = resp['port']
i += 1
time.sleep(1)
input()  # 等待手动登录
# resp = requests.get(f"http://localhost:5000/get_login_qrcode/{port}").json()
# print(resp)
# input()
# resp = requests.get(f"http://localhost:5000/get_login_info/{port}").json()
# print(resp)
# input()
# resp = requests.get(f"http://localhost:5000/get_contact_list/{port}").json()
# print(resp)
# input()
# post_data = {"wxid": "17926000072@chatroom"}
# resp = requests.post(f"http://localhost:5000/get_contact_details/{port}", json=post_data).json()
# print(resp)
# input()
# url = f"http://localhost:5000/send_file/{port}"
# files = {'file': open(r'D:\Pictures\a.jpg', 'rb')}
# post_data = {
#     "wxid": "filehelper"
# }
# resp = requests.post(url, data=post_data, files=files).json()
# print(resp)