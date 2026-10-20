import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

modelos = client.models.list()
print("Modelos ativos na sua conta NVIDIA:")
for m in modelos.data:
    if "instruct" in m.id:
        print(f" - {m.id}")