# PyWeChatSpy
help people make better use of WeChatForPC

相关文章：[硬核WeChatBot](https://zhuanlan.zhihu.com/p/118674498)

## 支持微信版本
### 3.0.0.57
微信客户端下载：[https://pan.baidu.com/s/1FIHQ4BCkpTSC-7QHk13LHw](https://pan.baidu.com/s/1FIHQ4BCkpTSC-7QHk13LHw) 提取码: v2n3

## 功能列表
### 基础功能
* 推送聊天消息 CHAT_MESSAGE
    * 回调结构 [ChatMessage](#ChatMessage)
* 获取登录账号信息 get_account_details
    * 回调结构 [AccountDetails](#AccountDetails)
* 发送文本 send_text
  * 入参
    * wxid 文本消息接收方wxid
    * text 文本内容  
    * at_wxid 需要被@的wxid(仅限群聊) at几个人,文本里就需要出现几个'@'符号 `spy.send_text('xxxx@chatroom', '@0000 @1111 Hello World', 'wxid_xxxx,wxid_yyyy')`
* 发送文件、图片 send_file
  * 入参
    * wxid 文件接收方wxid
    * file_path 文件路径
* 解密微信图片文件 decrypt_image(微信的图片下载到本地是加密的，需要使用此方法解密后方能看到图片原始内容)
  * 入参
    * source_file 带解密图片文件
    * target_file 解密后图片保存路径
### 高级功能
* 获取联系人列表 get_contacts(获取所有联系人，包括好友与群，不活跃的群可能无法获取)
  * 回调类型 CONTACTS_LIST
  * 回调结构 [Contacts](#Contacts)
* 获取联系人详情、群成员列表 get_contact_details
  * 入参
    * 联系人wxid
  * 回调类型 CONTACT_DETAILS  
  * 回调结构 [Contacts](#Contacts)
* 发送群公告 send_announcement
  * 入参
    * wxid 群wxid
    * content 公告内容
* 自动通过好友请求 accept_new_contact
  * 入参
    * encryptusername 好友请求Xml消息结构体同名字段值
    * ticket 好友请求Xml消息结构体同名字段值
* 设置联系人备注 set_remark
  * 入参
    * wxid 联系人wxid
    * remark 备注内容
* 分享群聊 share_chatroom
  * 入参
    * chatroom_wxid 待分享群聊wxid
    * wxid 联系人wxid
* 移除群成员 remove_chatroom_member
  * 入参
    * chatroom_wxid 待移除成员群聊wxid
    * wxid 待移除群聊成员wxid
* 移除联系人 remove_contact
  * 入参
    * wxid 待移除联系人wxid
* 发送小程序 send_mini_program
  * 入参
    * wxid 接收方wxid
    * title 小程序标题
    * image_path 小程序封面
    * route 小程序跳转路由，抓包小程序消息获取pagepath或自行生成
    * app_id 小程序AppId
    * username 小程序源Id
    * weappiconurl 小程序图标url
    * appname 小程序名称
* 发送链接卡片 send_link_card
  * 入参
    * wxid 接收方wxid
    * title 卡片标题
    * desc 卡片描述
    * app_id 卡片AppId
    * url 卡片跳转url
    * image_path 卡片封面图片路径
* 创建群聊 create_chatroom
  * 入参
    * wxid 创建群聊拉取的联系人wxid，不包括自己，至少连个，英文逗号分隔
  * 回调结构 [CreateGroupCallback](#CreateGroupCallback)
* 设置群名称 set_chatroom_name
  * 入参
    * wxid 待改名群聊wxid
    * name 群聊名称
* 推送群成员详情 GROUP_MEMBER_DETAILS
  * 回调结构 [GroupMemberDetails](#GroupMemberDetails)
* 推送群成员变动(进群&退群) GROUP_MEMBER_EVENT
  * 回调结构 [GroupMemberEvent](#GroupMemberEvent)
* 获取登录二维码 get_login_qrcode
  * 回调结构 [LoginQRCode](#LoginQRCode)
* 发送个人名片 send_card
  * 入参
    * wxid 名片接收wxid
    * card_wxid 名片wxid
    * card_nickname 名片显示昵称

## 数据结构
### <span id="AccountDetails">登录信息 AccountDetails</span> `account_details = spy_pb2.AccountDetails()`
* wxid 登录账号wxid `account_details.wxid`
* nickname 登录账号昵称 `account_details.nickname`
* wechatid 登录账号微信号 `account_details.wechatid`
* autograph 登录账号签名 `account_details.autograph`
* profilePhotoHD 登录账号高清头像 `account_details.profilePhotoHD`
* profilePhoto 登录账号头像 `account_details.profilePhoto`
* phone 登录账号绑定手机号 `account_details.phone`
* email 登录账号绑定邮箱 `account_details.email`
* qq 登录账号绑定QQ `account_details.qq`
* sex 登录账号性别 1男/2女 `account_details.sex`
* city 登录账号所在城市 `account_details.city`
* province 登录账号所在省份 `account_details.province`
* country 登录账号所在国家 `account_details.country`

### <span id="Contacts">Contacts</span> 联系人列表 `contacts_list = spy_pb2.Contacts()`
* contactDetails 联系人详情(可遍历) `for contact in contacts_list.contactDetails`
  * wxid 联系人wxid结构 `contact.wxid`
    * str 联系人wxid `contact.wxid.str`
  * nickname 联系人昵称结构 `contact.nickname`
    * str 联系人昵称 `contact.nickname.str`
  * sex 联系人性别 1男/2女 `contact.sex`
  * remark 联系人备注结构 `contact.remark`
    * str 联系人备注 `contact.remark.str`
  * wechatId 联系人微信号 `contact.wechatId`
  * groupOwnerWxid 群主wxid(如果联系人是群聊 wxid以"@chatroom"结尾) `cotact.groupOwnerWxid`
  * profilePhotoHD 联系人高清头像 `cotact.profilePhotoHD`
  * profilePhoto 联系人头像 `contact.profilePhoto`
  * groupMemberList 群成员列表(如果联系人是群聊 wxid以"@chatroom"结尾) `contact.groupMemberList`
    * memberCount 群成员数量 `contact.groupMemberList.memberCount`
    * groupMember 群成员信息(可遍历) `for member in contacts_list.contactDetails.groupMemberList.groupMember`
      * wxid 群成员wxid `member.wxid`
      * nickname 群成员昵称 `member.nickname`

### <span id="ChatMessage">ChatMessage</span> 微信消息 `chat_message = spy_pb2.ChatMessage()`
* message 微信消息(可遍历) `for message in chat_message.message`
  * wxidFrom 消息发送方wxid结构 `message.wxidFrom`
    * str 消息发送方wxid `message.wxidFrom.str`
  * wxidTo 消息接收方wxid结构 `message.wxidTo`
    * str 消息接收方 `message.wxidTo.str`
  * type 消息类型 1文本3图片43视频49Xml37好友请求10000系统消息... `message.type`
  * content 消息内容结构 `message.content`
    * str 消息内容 `message.content.str`
  * timestamp 消息时间戳 `message.timestamp`
  * head 消息头 `message.head`
  * file 消息附带文件(图片、视频等) `message.file`
  
### <span id="GroupMemberDetails">GroupMemberDetails</span> 群成员详情 `group_member_details = spy_pb2.GroupMemberDetails()`
* wxid 群wxid `group_member_details.wxid`
* detailsCount 详情数量(非群成员数量) `group_member_details.detailsCount`
* groupMemberDetails 群成员详情(可遍历) `for member_details in group_member_details.groupMemberDetails`
  * wxid 群成员wxid `member_details.wxid`
  * nickname 群成员昵称 `member_details.nickname`
  * groupNickname 群成员群内昵称 `member_details.groupNickname`
  * profilePhotoHD 群成员高清头像 `member_details.profilePhotoHD`
  * profilePhoto 群成员头像 `member_details.profilePhoto`
  * inviterWxid 群成员邀请人wxid `member_details.inviterWxid`
  
### <span id="GroupMemberEvent">GroupMemberEvent</span> 群成员变动事件 `group_member_event = spy_pb2.GroupMemberEvent()`
* wxid 群wxid `group_member_event.wxid`
* wxidJoin 进群wxid(可遍历) `for _join in group_member_event.wxidJoin`
* wxidLeave 退群wxid(可遍历) `for _leave in group_member_event.wxidLeave`

### <span id="CreateGroupCallback">CreateGroupCallback</span> 创建群聊回调 `callback = spy_pb2.CreateGroupCallback()`
* wxid 群聊wxid结构 `callback.wxid`
  * str 群聊wxid `callback.wxid.str`
  
### <span id="LoginQRCode">LoginQRCode</span> 登录二维码 `qrcode = spy_pb2.LoginQRCode()`
* qrcodeSize 二维码大小 `qrcode.qrcodeSize`
* qrcodeBytes 二维码数据 `qrcode.qrcodeBytes`

## 例子
### 一、本地运行
示例代码见[example.py](https://github.com/veikai/PyWeChatSpy/blob/master/example.py)

### 二、HTTP调用服务端
示例代码见
[service_example.py](https://github.com/veikai/PyWeChatSpy/blob/master/service_example.py)
和
[client_example.py](https://github.com/veikai/PyWeChatSpy/blob/master/client_example.py)

### 三、远程过程调用(RPC)
起作用的有4个额外文件：
* example_rpc_server.py
* example_rpc_client.py
* rpc_server_tools.py
* rpc_client_tools.py

使用方法：
1. 运行服务端 [example_rpc_server.py](https://github.com/veikai/PyWeChatSpy/blob/master/example_rpc_server.py) 启动微信
2. 运行客户端 [example_rpc_client.py](https://github.com/veikai/PyWeChatSpy/blob/master/example_rpc_client.py) 接收并处理消息

*注意：例子中，客户端和服务端在一台机子上，所以监听的ip是127.0.0.1，如果将客户端放到其他机器，请填写实际服务端对应的ip，出现端口冲突的话也可以灵活更改端口，并配置对应服务器防火墙放行*

### 四、其他例子

__待补充，欢迎大家贡献！__