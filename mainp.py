from llm.client import OpenRouterLLM

llm = OpenRouterLLM()

response = llm.generate(
    "What is photosynthesis? Answer in one sentence."
)

print(response)