from openai import AsyncOpenAI
from config import OPENAI_API_KEY, MODELS, SYSTEM_PROMPT

class ChatGPTModel:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = MODELS['chatgpt']
    
    async def generate_response(self, prompt, history=None):
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            if history:
                messages.extend(history[-10:])  # 保留最近10条消息
            
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ ChatGPT错误: {str(e)}"