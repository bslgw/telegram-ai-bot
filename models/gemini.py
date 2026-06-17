import google.generativeai as genai
from config import GEMINI_API_KEY, SYSTEM_PROMPT

class GeminiModel:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def generate_response(self, prompt, history=None):
        try:
            # 构建对话历史
            chat_history = []
            
            if history:
                for msg in history[-10:]:  # 保留最近10条消息
                    role = "user" if msg['role'] == 'user' else "model"
                    chat_history.append({
                        "role": role,
                        "parts": [msg['content']]
                    })
            
            # 创建聊天会话
            chat = self.model.start_chat(history=chat_history)
            
            # 发送消息并获取响应
            response = chat.send_message(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2000,
                )
            )
            
            return response.text
        except Exception as e:
            return f"❌ Gemini错误: {str(e)}"