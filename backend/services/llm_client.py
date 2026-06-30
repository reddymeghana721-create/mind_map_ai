from openai import OpenAI

class OpenRouterLLM:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="YOUR_API_KEY"  # replace this
        )

    def generate(self, prompt):
        response = self.client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content