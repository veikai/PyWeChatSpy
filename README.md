# PyWeChatSpy
help people make better use of WeChatForPC

相关文章：[硬核WeChatBot](https://zhuanlan.zhihu.com/p/118674498)

## 支持微信版本
### 3.0.0.57
微信客户端下载：[https://pan.baidu.com/s/1FIHQ4BCkpTSC-7QHk13LHw](https://pan.baidu.com/s/1FIHQ4BCkpTSC-7QHk13LHw) 提取码: v2n3

## 功能列表
### 基础功能
* 获取聊天消息
* 获取登录账号信息 get_account_details
* 发送文本 send_text
* 发送文件、图片 send_file
* 解密微信图片文件 decrypt_image
    * 微信的图片下载到本地是加密的，需要使用此方法解密后方能看到图片原始内容
### 高级功能
* 获取联系人列表 get_contacts
    * 获取所有联系人，包括好友与群，不活跃的群可能无法获取
* 获取联系人详情、群成员列表 get_contact_details
* 发送群公告 send_announcement
* 自动通过好友请求 accept_new_contact
* 设置联系人备注 set_remark
* 分享群聊 share_chatroom
* 移除群成员 remove_chatroom_member
* 移除联系人 remove_contact
* 发送小程序 send_mini_program
* 发送链接卡片 send_link_card
* 创建群聊 create_chatroom
* 设置群名称 set_chatroom_name
* 推送群成员详情 GROUP_MEMBER_DETAILS
* 推送群成员变动(进群&退群) GROUP_MEMBER_EVENT

示例代码见example.py