import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenRouterLLM:

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if self.api_key and not self.api_key.startswith("your_"):
            try:
                self.client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.api_key,
                    timeout=5.0
                )
            except Exception:
                self.client = None
        else:
            self.client = None

<<<<<<< Updated upstream:backend/services/llm_client.py
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
=======
    def generate(self, prompt):
        if not self.client:
            return ""

        try:
            response = self.client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[OpenRouterLLM] Exception: {e}")
            return ""
>>>>>>> Stashed changes:backend/services/llm/client.py
