import json
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from config import TELEGRAM_TOKEN, MODELS, DEFAULT_MODEL
from models import ChatGPTModel, GeminiModel, DeepSeekModel

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 初始化AI模型
ai_models = {
    'chatgpt': ChatGPTModel(),
    'gemini': GeminiModel(),
    'deepseek': DeepSeekModel()
}

# 用户数据管理
class UserManager:
    def __init__(self, data_file='user_data.json'):
        self.data_file = data_file
        self.users = self.load_data()
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def get_user(self, user_id):
        user_id = str(user_id)
        if user_id not in self.users:
            self.users[user_id] = {
                'model': DEFAULT_MODEL,
                'history': [],
                'message_count': 0
            }
            self.save_data()
        return self.users[user_id]
    
    def set_model(self, user_id, model):
        user_id = str(user_id)
        if model in MODELS:
            self.users[user_id]['model'] = model
            self.save_data()
            return True
        return False
    
    def add_to_history(self, user_id, role, content):
        user_id = str(user_id)
        user = self.get_user(user_id)
        user['history'].append({'role': role, 'content': content})
        user['message_count'] += 1
        # 限制历史记录长度
        if len(user['history']) > 20:
            user['history'] = user['history'][-20:]
        self.save_data()
    
    def get_stats(self, user_id):
        user = self.get_user(user_id)
        return {
            'model': user['model'],
            'message_count': user['message_count'],
            'history_length': len(user['history'])
        }

user_manager = UserManager()

# ========== 权限控制 ==========
ALLOWED_USER_ID = 722871213  # 你的 Telegram 用户 ID

def restricted(func):
    """装饰器：只允许指定用户使用"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != ALLOWED_USER_ID:
            await update.effective_message.reply_text("⛔ 私人项目，禁止访问")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# 命令处理
@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送欢迎消息"""
    welcome_text = (
        "🤖 *欢迎使用多模型AI机器人！*\n\n"
        "🚀 *可用命令：*\n"
        "/start \\- 显示此消息\n"
        "/model \\- 切换AI模型\n"
        "/clear \\- 清除对话历史\n"
        "/stats \\- 查看统计信息\n"
        "/help \\- 帮助信息\n\n"
        "💬 直接发送消息即可与AI对话！\n"
        "🔄 支持模型：ChatGPT \\| Gemini \\| DeepSeek"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🤖 ChatGPT", callback_data="model_chatgpt"),
            InlineKeyboardButton("🌟 Gemini", callback_data="model_gemini")
        ],
        [InlineKeyboardButton("🔮 DeepSeek", callback_data="model_deepseek")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='MarkdownV2'
    )

@restricted
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """帮助信息"""
    help_text = (
        "📚 *使用说明*\n\n"
        "1️⃣ 直接发送消息与AI对话\n"
        "2️⃣ 使用 /model 命令切换AI模型\n"
        "3️⃣ 使用 /clear 清除对话历史\n"
        "4️⃣ 使用 /stats 查看使用统计\n\n"
        "*支持的模型：*\n"
        "• 🤖 ChatGPT \\(GPT\\-3\\.5\\)\n"
        "• 🌟 Gemini Pro\n"
        "• 🔮 DeepSeek Chat\n\n"
        "*提示：*\n"
        "• 机器人会记住最近20条对话\n"
        "• 切换模型不会清除历史\n"
        "• 长回复会自动分段发送"
    )
    await update.message.reply_text(help_text, parse_mode='MarkdownV2')

@restricted
async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """模型切换菜单"""
    user_id = update.effective_user.id
    current_model = user_manager.get_user(user_id)['model']
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅ ' if current_model == 'chatgpt' else ''}ChatGPT",
                callback_data="model_chatgpt"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅ ' if current_model == 'gemini' else ''}Gemini",
                callback_data="model_gemini"
            )
        ],
        [
            InlineKeyboardButton(
                f"{'✅ ' if current_model == 'deepseek' else ''}DeepSeek",
                callback_data="model_deepseek"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🤖 *当前模型：{current_model}*\n\n请选择要切换的模型：",
        reply_markup=reply_markup,
        parse_mode='MarkdownV2'
    )

@restricted
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看统计信息"""
    user_id = update.effective_user.id
    stats = user_manager.get_stats(user_id)
    
    stats_text = (
        "📊 *使用统计*\n\n"
        f"• 当前模型：{stats['model']}\n"
        f"• 消息总数：{stats['message_count']}\n"
        f"• 历史长度：{stats['history_length']}"
    )
    
    await update.message.reply_text(stats_text, parse_mode='MarkdownV2')

@restricted
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理按钮回调"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    
    if callback_data.startswith("model_"):
        model = callback_data.replace("model_", "")
        if user_manager.set_model(user_id, model):
            model_names = {
                'chatgpt': '🤖 ChatGPT',
                'gemini': '🌟 Gemini',
                'deepseek': '🔮 DeepSeek'
            }
            model_name = model_names.get(model, model)
            await query.edit_message_text(f"✅ 已切换到 {model_name} 模型")
        else:
            await query.edit_message_text("❌ 切换失败，模型不存在")

@restricted
async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """清除对话历史"""
    user_id = str(update.effective_user.id)
    if user_id in user_manager.users:
        user_manager.users[user_id]['history'] = []
        user_manager.save_data()
    await update.message.reply_text("✅ 对话历史已清除")

@restricted
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户消息"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # 获取用户数据和当前模型
    user_data = user_manager.get_user(user_id)
    current_model = user_data['model']
    history = user_data['history']
    
    # 发送"正在输入"状态
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # 添加用户消息到历史
    user_manager.add_to_history(user_id, 'user', user_message)
    
    # 获取AI响应
    model_instance = ai_models.get(current_model)
    if model_instance:
        try:
            response = await model_instance.generate_response(user_message, history)
            # 添加AI响应到历史
            user_manager.add_to_history(user_id, 'assistant', response)
        except Exception as e:
            logger.error(f"Model error: {e}")
            response = "❌ AI服务暂时不可用，请稍后再试"
    else:
        response = "❌ 错误：未找到指定的AI模型"
    
    # 发送响应（支持长消息分段）
    max_length = 4000
    if len(response) > max_length:
        for i in range(0, len(response), max_length):
            await update.message.reply_text(
                response[i:i+max_length],
                parse_mode=None  # 长消息不使用Markdown避免格式错误
            )
    else:
        # 尝试使用Markdown，如果失败则发送纯文本
        try:
            await update.message.reply_text(response, parse_mode='Markdown')
        except:
            await update.message.reply_text(response)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """错误处理"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # 如果是CallbackQuery相关的错误
    if update and isinstance(update, Update) and update.callback_query:
        try:
            await update.callback_query.answer("发生错误，请重试")
        except:
            pass
    
    # 发送错误消息给用户
    if update and isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ 抱歉，发生了错误，请稍后再试"
            )
        except:
            pass

def main():
    """启动机器人"""
    # 检查Token
    if not TELEGRAM_TOKEN:
        logger.error("未设置TELEGRAM_TOKEN！请在.env文件中配置")
        return
    
    # 创建应用
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("model", model_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # 添加回调查询处理器
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # 添加消息处理器（处理所有文本消息，但不处理命令）
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    # 添加错误处理器
    application.add_error_handler(error_handler)
    
    # 设置输入框左侧菜单按钮
    from telegram import BotCommand
    
    async def set_menu(app):
        commands = [
            BotCommand("start", "🚀 开始 / 切换引擎"),
            BotCommand("model", "🔄 切换AI模型"),
            BotCommand("clear", "🧹 清除对话历史"),
            BotCommand("stats", "📊 查看统计"),
            BotCommand("help", "📚 帮助信息"),
        ]
        await app.bot.set_my_commands(commands)
        await app.bot.set_chat_menu_button()
    
    application.post_init = set_menu
    
    # 启动机器人
    logger.info("🤖 机器人启动中...")
    print("🤖 机器人已启动！按 Ctrl+C 停止")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()