import requests
import base64

resp = requests.get("http://localhost:5000/open_wechat").json()
print(resp)
input()  # 等待手动登录
resp = requests.get("http://localhost:5000/get_account_info/0").json()
print(resp)
input()
resp = requests.get("http://localhost:5000/get_contacts/0").json()
print(resp)
