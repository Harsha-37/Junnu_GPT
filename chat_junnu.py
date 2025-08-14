# chat_junnu.py
import os
from dotenv import load_dotenv
from openai import OpenAI
from junnu_persona import system_prompt, few_shot_examples

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def init_messages():
    # Same as your CLI: system + few-shot
    return [{"role": "system", "content": system_prompt}] + list(few_shot_examples)

def chat_once(messages, user_text, model="gpt-4o"):
    # append user, call OpenAI, append assistant, return reply
    messages.append({"role": "user", "content": user_text})
    resp = client.chat.completions.create(model=model, messages=messages)
    reply = resp.choices[0].message.content.strip()
    messages.append({"role": "assistant", "content": reply})
    return reply, messages


