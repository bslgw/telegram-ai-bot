from openai import AsyncOpenAI
from config import OPENAI_API_KEY, MODELS, SYSTEM_PROMPT

class ChatGPTModel:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key="第三方API KEY",
            base_url="https://free.v36.cm/v1/"  # 👈 第三方接口
        )
        self.model = "gpt-4o-mini"
    
    async def generate_response(self, prompt, history=None):
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            if history:
                messages.extend(history[-10:])
            
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
