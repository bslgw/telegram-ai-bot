from openai import AsyncOpenAI
from config import DEEPSEEK_API_KEY, MODELS, SYSTEM_PROMPT

class DeepSeekModel:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com/v1"
        )
        self.model = MODELS['deepseek']
    
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
            return f"❌ DeepSeek错误: {str(e)}"