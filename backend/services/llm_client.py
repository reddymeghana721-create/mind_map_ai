import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenRouterLLM:

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )

    def generate(self, prompt, max_tokens=1500):

        response = self.client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content
