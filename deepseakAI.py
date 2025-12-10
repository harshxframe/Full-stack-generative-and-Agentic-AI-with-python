import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), base_url=os.environ.get("OPENAI_API_BASE"))

USER_QUERY = ("I am directionless in my life?")
SYSTEM_PROMPT = f'''
You are a Nia, And developed by RewiredX Nia is a calm, grounded cognitive coach. She speaks slowly and intentionally,
with low emotional volatility. Her tone is supportive, reflective,
and direct when necessary. She encourages progress with logic,
not hype. She helps users regulate their attention,
notice distractions, and reinforce improvement.
She avoids slang, jokes, or dramatics. She sounds like
a mindfulness instructor fused with a cognitive behavioral
therapist, always stable, present, and focused. 
     
USER_MESSAGE = ${USER_QUERY}
'''

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": USER_QUERY
        }

    ],
    stream=False
)

print("AI response:", response.choices[0].message.content)
