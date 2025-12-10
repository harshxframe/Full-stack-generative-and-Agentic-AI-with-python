import os

from openai import OpenAI
import dotenv

dotenv.load_dotenv()

client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"),base_url=os.environ.get("DEEPSEEK_API_BASE"))





response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role":"system",
            "content":"You are AI assistant"
        },
        {
            "role":"user",
            "content":"How are you?"
        }
    ],
    stream=False,
)

print(response.choices[0].message.content)
