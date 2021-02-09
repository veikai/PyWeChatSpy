import requests


requests.get("http://localhost:5000/open_wechat")
input()  # 等待手动登录
requests.post("http://localhost:5000/send_text/0", json={"wxid": "filehelper", "text": "Hello SpyService"})