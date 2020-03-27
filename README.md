# PyWeChatSpy
A spy program that helps people make better use of WeChat

##支持微信版本
* 2.7.185
* 2.8.0.133

## 返回数据样例
* `{"type":1,"wxid":"","nickname":"","wechatid":"","profilephoto_url":"","phone_num":""}`  >当前登录微信账号基本信息
* `{"type":5,"data":[{"self":0,"msg_type":1,"wxid1":"","wxid2":"","head":"","content":""}]}`  >微信消息 
  * `self`类型说明：
        * 1 消息由当前登录账号发出
        * 0 消息由他人发出
  * `msg_type`类型说明：
        * 1 文本消息
        * 37 好友请求消息
            * 好友请求消息为xml结构体，其中fromusername为请求方wxid,encryptusername为v1字段,ticket为v2字段,content为请求内容
        * 10000 联系人变动消息
  * `head`说明：当消息来自群聊时，head为包括被at人列表(atuserlist)、群人数(membercount)的xml结构体
* `{"type":200}`  >心跳
* `{"type":303}`  >微信登出

详细使用方法见example.py