# SpyService接口文档

## 1. 打开微信
### 1.1 功能描述
唤起微信客户端并返回微信客户端标识port
### 1.2 请求说明
> 请求方式：GET<br>
请求URL ：[/open_wechat]()

### 1.3 请求参数
无
### 1.4 返回结果
```json 
{
  "code": 1,
  "port": 50866
}
```
### 1.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
port       |int        |微信客户端标识
### 1.6 状态码
状态码       |说明
------------|-----------
1       |成功
0       |失败
---
## 2. 获取登录二维码
### 2.1 功能描述
获取微信登录二维码供用户扫码登录
### 2.2 请求说明
> 请求方式：GET<br>
请求URL ：[/get_login_qrcode/\<int:port\>]()

### 2.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
### 2.4 返回结果
```json 
{
  "code": 1,
  "qrcode": "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"
}
```
### 2.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
qrcode     |string     |登录二维码base64编码字符串
### 2.6 状态码
状态码       |说明
------------|-----------
0       |获取二维码超时
-1       |port错误
1       |成功
---
## 3. 登出微信
### 3.1 功能描述
用户主动退出PC微信客户端登录
### 3.2 请求说明
> 请求方式：GET<br>
请求URL ：[/user_logout/\<int:port\>]()

### 3.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
### 3.4 返回结果
```json 
{
  "code": 1
}
```
### 3.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 3.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
1       |成功
---
## 4. 关闭微信客户端
### 4.1 功能描述
用户关闭服务器上的微信客户端
### 4.2 请求说明
> 请求方式：GET<br>
请求URL ：[/close_wechat/\<int:port\>]()

### 4.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
### 4.4 返回结果
```json 
{
  "code": 1
}
```
### 4.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 4.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
1       |成功
---
## 5. 获取微信登录状态
### 5.1 功能描述
获取微信登录状态
### 5.2 请求说明
> 请求方式：GET<br>
请求URL ：[/get_login_status/\<int:port\>]()

### 5.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
### 5.4 返回结果
```json 
{
  "code": 1,
  "status": "0"
}
```
### 5.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
status     |string     |登录状态 "0":未登录/'1":登录
### 5.6 状态码
状态码       |说明
------------|-----------
0       |获取二维码超时
-1       |port错误
1       |成功
---
## 6. 获取登录信息
### 6.1 功能描述
获取用户当前登录微信账号基本信息
### 6.2 请求说明
> 请求方式：GET<br>
请求URL ：[/get_login_info/\<int:port\>]()

### 6.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
### 6.4 返回结果
```json 
{
  "code": 1,
  "wxid": "",
  "nickname":"",
  "wechatid":"",
  "profile_photo_hd":"",
  "profile_photo":"",
  "phone":"",
  "sex":""
}
```
### 6.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
wxid     |string     |微信唯一标识
nickname     |string     |昵称
wechatid     |string     |微信号
profile_photo_hd     |string     |高清头像url
profile_photo     |string     |头像url
phone     |string     |手机号
sex     |string     |性别
### 6.6 状态码
状态码       |说明
------------|-----------
0       |获取登录信息超时
-1       |port错误
1       |成功
---
## 7. 获取联系人列表
### 7.1 功能描述
获取微信联系人列表，包括好友与群
### 7.2 请求说明
> 请求方式：GET<br>
请求URL ：[/get_contact_list/\<int:port\>]()

### 7.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
### 7.4 返回结果
```json 
{
  "code": 1,
  "contacts": [{"wxid":"", "nickname":"", "remark":""},.....]
}
```
### 7.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
contacts     |list     |联系人列表

字段       |字段类型       |字段说明
------------|-----------|-----------
wxid       |string        |联系人微信唯一标识
nickname     |string     |联系人昵称
remark     |string     |联系人备注

### 7.6 状态码
状态码       |说明
------------|-----------
0       |获取联系人列表超时
-1       |port错误
1       |成功
---
## 8. 获取联系人详情
### 8.1 功能描述
获取联系人、群成员详情或获取群成员列表
### 8.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/get_contact_details/\<int:port\>]()

### 8.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |联系人唯一标识
### 8.4 返回结果
```json 
{
  "code": 1,
  "wxid": "",
  "nickname":"",
  "remark":"",
  "profile_photo:"",
  "is_group":False,
  "group_owner":"",
  "group_member_count":0,
  "group_members":[{"wxid":"", "nickname":""},......]
}
```
### 8.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
wxid     |string     |联系人唯一标识
nickname     |string     |联系人昵称
remark     |string     |联系人备注
profile_photo     |string     |联系人头像
is_group     |bool     |该联系人是否为群聊
group_owner     |string     |群主
group_member_count     |int     |群成员数量
group_members     |list     |群成员列表

字段       |字段类型       |字段说明
------------|-----------|-----------
wxid       |string        |群成员微信唯一标识
nickname     |string     |群成员微信昵称
### 8.6 状态码
状态码       |说明
------------|-----------
0       |获取联系人详情超时
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---
## 9. 发送文本
### 9.1 功能描述
发送文本消息给指定联系人
### 9.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/send_text/\<int:port\>]()

### 9.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |消息接收方唯一标识
text       |string     |消息内容
at_wxid    |string     |消息需@提醒人唯一标识
### 9.4 返回结果
```json 
{
  "code": 1
}
```
### 9.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 9.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---
## 10. 发送文件
### 10.1 功能描述
发送文件、图片消息
### 10.2 请求说明
> 请求方式：POST(form)<br>
请求URL ：[/send_file/\<int:port\>]()

### 10.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |消息接收方唯一标识
file       |file       |文件
### 10.4 返回结果
```json 
{
  "code": 1
}
```
### 10.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 10.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-4       |请求参数提交模式错误,应当以表单提交
-3       |请求参数缺失
1       |成功
---
## 11. 发布群公告
### 11.1 功能描述
发布群公告
### 11.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/send_announcement/\<int:port\>]()

### 11.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |群唯一标识
text       |string     |群公告内容
### 11.4 返回结果
```json 
{
  "code": 1
}
```
### 11.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 11.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---
## 12. 接收好友请求
### 12.1 功能描述
通过新联系人好友验证
### 12.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/verify_new_contact/\<int:port\>]()

### 12.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
encryptusername       |string        |好友验证参数1
ticket       |string        |好友验证参数2
### 12.4 返回结果
```json 
{
  "code": 1
}
```
### 12.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 12.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---
## 13. 设置联系人备注
### 13.1 功能描述
设置、修改联系人备注
### 13.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/set_remark/\<int:port\>]()

### 13.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |联系人唯一标识
remark     |string     |备注
### 13.4 返回结果
```json 
{
  "code": 1
}
```
### 13.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 13.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---
## 14. 分享群聊
### 14.1 功能描述
发送群聊邀请链接给指定好友
### 14.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/share_chatroom/\<int:port\>]()

### 14.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |好友唯一标识
group_wxid |string     |群聊唯一标识
### 14.4 返回结果
```json 
{
  "code": 1
}
```
### 14.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 14.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---
## 15. 移除群成员
### 15.1 功能描述
从群聊中将指定群成员移出该群
### 15.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/remove_chatroom_member/\<int:port\>]()

### 15.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
group_wxid |string     |群聊唯一标识
wxid       |string     |群成员唯一标识
### 15.4 返回结果
```json 
{
  "code": 1
}
```
### 15.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 15.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---
## 16. 移除联系人
### 16.1 功能描述
删除指定好友
### 16.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/remove_contact/\<int:port\>]()

### 16.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |好友唯一标识
### 16.4 返回结果
```json 
{
  "code": 1
}
```
### 16.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 16.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---
## 17. 发送小程序
### 17.1 功能描述
发送小程序给指定联系人
### 17.2 请求说明
> 请求方式：POST(form)<br>
请求URL ：[/send_mini_program/\<int:port\>]()

### 17.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |联系人唯一标识
title      |string     |小程序标题
app_id     |string     |小程序id
route      |string     |小程序路由
username   |string     |小程序用户名
weappiconurl|string    |小程序图标url
appname    |string     |小程序名称
### 17.4 返回结果
```json 
{
  "code": 1
}
```
### 17.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 17.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-4       |请求参数提交模式错误,应当以表单提交
-3       |请求参数缺失
1       |成功
---
## 18. 发送链接卡片
### 18.1 功能描述
发送链接卡片给指定联系人
### 18.2 请求说明
> 请求方式：POST(form)<br>
请求URL ：[/send_link_card/\<int:port\>]()

### 18.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |联系人唯一标识
title      |string     |链接卡片标题
desc       |string     |链接卡片描述
url        |string     |链接卡片链接
app_id     |string     |链接卡片id
### 18.4 返回结果
```json 
{
  "code": 1
}
```
### 18.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 18.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-4       |请求参数提交模式错误,应当以表单提交
-3       |请求参数缺失
1       |成功
---
## 19. 解密图片
### 19.1 功能描述
将接收到的图片解密成jpg格式
### 19.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/decrypt_image/\<int:port\>]()

### 19.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
filename   |string     |图片加密文件名称
### 19.4 返回结果
解密后图片bytes
### 19.5 返回参数

### 19.6 状态码

---
## 20. 新建群聊
### 20.1 功能描述
创建一个新的群聊
### 20.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/create_chatroom/\<int:port\>]()

### 20.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxids      |string     |联系人wxid合集字符串 ","分隔
### 20.4 返回结果
```json 
{
  "code": 1,
  "wxid": ""
}
```
### 20.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
wxid     |string     |新群聊唯一标识
### 20.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---
## 21. 设置群聊名称
### 21.1 功能描述
设置、修改群聊名称
### 21.2 请求说明
> 请求方式：POST(json)<br>
请求URL ：[/set_chatroom_name/\<int:port\>]()

### 21.3 请求参数
字段       |字段类型       |字段说明
------------|-----------|-----------
port       |int        |微信客户端标识
wxid       |string     |群聊唯一标识
name       |string     |群聊名称
### 21.4 返回结果
```json 
{
  "code": 1
}
```
### 21.5 返回参数
字段       |字段类型       |字段说明
------------|-----------|-----------
code       |int        |状态码
### 21.6 状态码
状态码       |说明
------------|-----------
0       |失败
-1       |port错误
-2       |请求参数提交模式错误,应当以json提交
-3       |请求参数缺失
1       |成功
---