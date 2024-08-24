# Telegram Shell Bot

该项目是一个基于 Telegram 的机器人，用于通过 SSH 管理服务器。

## 功能特性

- 添加、删除服务器，并将服务器绑定到具体的 Telegram 用户。
- 选择服务器并在其上执行 Shell 命令。
- 获取服务器的基本信息，包括 CPU、内存、磁盘、负载等。
- 支持非 22 端口的 SSH 连接。
- 支持使用 SSH 密钥文件进行身份验证。
- 所有敏感信息如服务器密码均加密存储，使用自定义加密 Token 进行加密和解密。
- 取消选择服务器的功能。
- 只有在选择服务器的情况下，才能执行命令。

## 项目结构

```plaintext
telegram_bot/
│
├── bot.py               # 主程序入口
├── commands/
│   ├── __init__.py      # 命令模块初始化
│   ├── add_server.py    # 添加服务器
│   ├── remove_server.py # 删除服务器
│   ├── list_servers.py  # 列出服务器
│   ├── exec_command.py  # 执行命令
│   ├── server_status.py # 获取服务器状态
│   ├── cancel_selection.py  # 取消选择服务器
│
├── utils/
│   ├── __init__.py      # 工具模块初始化
│   ├── encryption.py    # 加密和解密工具
│   ├── db.py            # 数据库管理工具
│   ├── logging.py       # 日志工具
│
├── data/
│   └── encrypted_db.sqlite  # 加密后的数据库文件
│
├── config.ini           # 配置文件，存储 Telegram API Token 和加密 Token
├── requirements.txt     # 依赖包列表
└── README.md            # 项目说明
```
# 安装和使用
## 克隆项目
```sh
git clone https://github.com/yourusername/telegram-shell-bot.git
cd telegram-shell-bot
```
## 安装依赖
```sh
pip install -r requirements.txt
```
## 配置
复制并修改 config.ini 文件，填入你的 Telegram API Token：
```plaintext
[telegram]
api_token = YOUR_TELEGRAM_API_TOKEN_HERE

[encryption]
key = YOUR_ENCRYPTION_KEY_HERE
```
api_token是从@botfather创建bot获取的api token，key会随机生成不用修改
## 运行
```sh
python bot.py
```
## 备份与迁移数据库文件
数据库文件在data/encrypted_db.sqlite下
## 命令
```sh
addServer
使用密码
/addserver <别名> <用户名> <主机> <密码或密钥> [<端口>] [<是否使用密钥>]
/addserver server1 root 192.168.1.10 mypassword 22 false
使用密钥
/addserver <别名> <用户名> <主机> <密码或密钥> [<端口>] [<是否使用密钥>]
/addserver server1 root 192.168.1.10 "your-ssh-private-key" 22 true
列出已添加的服务器
/listservers
查看服务器状态
/status
删除服务器
/removeserver <主机>
/removeserver 192.168.1.10
取消选择服务器
/cancelselection
执行命令(当选择完服务器后输入的字符串自动会当成命令执行)
ls -la /var/log
```
## License
此项目使用 MIT License，详情请参阅 LICENSE 文件。
