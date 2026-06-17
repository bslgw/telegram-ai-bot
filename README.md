# telegram-ai-bot

先编译安装python3.11

pip3 install -r requirements.txt

在 @BotFather 创建Telegram机器人获取Token

获取各AI服务的API密钥

编辑 .env 文件填入密钥

编辑bot.py    

ALLOWED_USER_ID = xxxxxxx  # 你的 Telegram 用户 ID ，只允许此用户id账号使用机器人

python3.11 bot.py

备注：openai 可以使用此项目提供的免费API   https://github.com/popjane/free_chatgpt_api
