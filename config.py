import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

# 模型配置
MODELS = {
    'chatgpt': 'gpt-3.5-turbo',
    'gemini': 'gemini-pro',
    'deepseek': 'deepseek-chat'
}

# 默认模型
DEFAULT_MODEL = 'chatgpt'

# 系统提示词
SYSTEM_PROMPT = "你是一个有帮助的AI助手，请用简洁清晰的语言回答问题。"