# PyWeChatSpy
A spy program that helps people make better use of WeChat

[硬核WeChatBot](https://zhuanlan.zhihu.com/p/118674498)

##支持微信版本
* 2.8.0.133

## 返回数据样例
* `{"type":1,"wxid":"","nickname":"","wechatid":"","profilephoto_url":"","phone_num":""}`  >微信登入、当前登录微信账号基本信息
* `{"type":2,"wxid":"","nickname":"","wechat_id":"",...}`  >联系人详情
* `{"type":3,"data":["wxid":"","nickname":"","remark":""],"step":50,"total_page":1,"current_page":1}`  >联系人列表
* `{"type":4,"data":["wxid":"", "nickname":""],"wxid":""}`  >群成员列表
* `{"type":5,"data":[{"self":0,"msg_type":1,"wxid1":"","wxid2":"","head":"","content":""}]}`  >微信消息 
  * `self`类型说明：
    * 1 消息由当前登录账号发出
    * 0 消息由他人发出
  * `msg_type`类型说明：
    * 1 文本
    * 3 图片
    * 37 好友申请
    * 42 名片
    * 43 视频
    * 47 表情
    * 48 位置
    * 49 各种推送、分享、文件、转账
    * 10000 系统消息
  * `wxid1` 消息来源可能是联系人好友也可能是群
  * `wxid2` 当消息来自群时 为具体群内发言成员
  * `content` 消息具体内容
* `{"type":6,"data":["wxid":"","nickname":"","remark":""],"step":50,"total_page":1,"current_page":1}`  >联系人最新信息
* `{"type":7,"wxid":"","status":0(正常)/-44(被删除)/-22(被拉黑)/-1(未知异常)}`  >联系人状态
* `{"type":8,"success":0失败/1成功,"qrcode_path":""}`  >登录二维码信息
* `{"type":100}`  >socket连接成功
* `{"type":200}`  >心跳 用于验证微信客户端与Spy连接状态
* `{"type":203}`  >微信登出
* `{"type":9527, "content":""}`  >系统提示

## 功能列表
* `query_login_info()`  >查询当前登录账号信息
* `query_contact_details(wxid)` >查询联系人详情
* `query_contact_list(step=50)` >查询联系人列表
    * `step` 联系人异步分批回调 每批回调联系人个数
* `query_chatroom_member(wxid)` >查询群成员列表
* `send_text(wxid, content, at_wxid="")` >发送文本
    * `at_wxid` 被@群成员wxid
* `send_file(wxid, file_path)` >发送文件
* `accept_new_contact(encryptusername, ticket)` >接受新联系人申请
    * `encryptusername、ticket` 好友申请xml消息体里的字段 自行解析xml可以得到
* `send_announcement(wxid, content)` >发送群公告
* `create_chatroom("wxid1,wxid2,...,wxidn")` >创建群聊
* `share_chatroom(chatroom_wxid, "wxid1,wxid2,...,wxidn")` >分享群聊邀请链接`
* `remove_chatroom_member(chatroom_wxid, "wxid1,wxid2,...,wxidn")`  >移除群成员
* `remove_contact(wxid)` >移除联系人
* `add_contact_from_chatroom(chatroom_wxid, wxid, msg)` >添加群成员为好友
* `add_unidirectional_contact_a(wxid, msg)`  >添加单向好友(对方删除自己)
* `add_unidirectional_contact_b(wxid)`  >添加单向好友(自己删除对方)
* `check_contact_status(wxid)`  >检查联系人状态(僵尸粉检测)
* `set_chatroom_name(wxid, name)`  >设置群聊名称
* `set_save_folder(folder)`  >手动同步微信下载文件保存路径
* `show_qrcode(output_path="")`  >展示登录二维码并将二维码图片保存到指定路径(默认当前工作路径)



详细使用方法见[example.py](https://github.com/veikai/PyWeChatSpy/blob/master/example.py)