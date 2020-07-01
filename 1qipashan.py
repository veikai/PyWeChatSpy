from PyWeChatSpy import WeChatSpy
from tencentcloud.common import credential
from tencentcloud.ocr.v20181119 import ocr_client, models
import base64


image_path = r"D:\18020891\GitHub\PyWeChatSpy\images\bqstz.jpg"


def my_parser(data):
    if data["type"] == 5:  # 判断是微信消息数据
        for msg in data["data"]:  # 遍历微信消息
            if not msg["self"]:  # 判断消息是否由他人发出
                if msg["msg_type"] == 1:  # 判断是否文本消息
                    print(msg["content"])
                    if "爬山" in msg["content"]:  # 判断是否去爬山
                        spy.send_file(msg["wxid1"], image_path)  # 发送图片
                elif msg["msg_type"] == 3:  # 判断是否图片消息
                    req = models.GeneralAccurateOCRRequest()
                    with open(msg["image_path"], "rb") as rf:  # 读取图片
                        base64_data = base64.b64encode(rf.read())  # 转化为base64
                        req.ImageBase64 = base64_data.decode()
                    cred = credential.Credential("secretId",
                                                 "secretKey")
                    client = ocr_client.OcrClient(cred, "ap-shanghai")
                    r = client.GeneralAccurateOCR(req)  # 识别图片
                    for item in r.TextDetections:
                        print(item.DetectedText)
                        if "爬山" in item.DetectedText:
                            spy.send_file(msg["wxid1"], image_path)  # 发送图片
                            break


spy = WeChatSpy(parser=my_parser)  # 实例化WeChatSpy类


if __name__ == '__main__':
    spy.run()  # 运行代码
