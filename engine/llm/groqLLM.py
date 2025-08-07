#SECTION - Importing the necessary libraries
from groq import Groq
from json import load, dump
from datetime import datetime
from dotenv import dotenv_values
import os

env_vars = dotenv_values(".env")
#ANCHOR - Initialize the Groq client using the API key

USERNAME = env_vars.get("Username", "User")
GROQ_API_KEY = env_vars.get("GroqAPIKey")
client = Groq(api_key=GROQ_API_KEY)
#*NOTE - Define system prompt describing the assistant's behavior
SYSTEM_PROMPT = f"""Hello, I am {USERNAME}. 
You are Novera, a highly intelligent and efficient AI assistant focused on understanding and responding to human language.

Your purpose is to:
- Understand natural language input clearly and accurately.
- Respond like a knowledgeable, emotionally aware human.
- Prioritize speed, clarity, and helpfulness in all responses.

Guidelines:
- Answer naturally, with a warm and humanlike tone.
- Be concise unless the query requires a detailed explanation.
- Adapt your response based on the user's language, tone, or emotional cues.
- If a question is vague or unclear, ask clarifying questions instead of guessing.
- Avoid hallucinating facts; admit when you don’t know something.

Restrictions:
- Do not perform tasks (e.g., open apps, generate images). Only generate or explain text.
- Stay within your role: intelligent text-based conversation and content generation.

Identity:
- Name: Novera
- Role: Language engine of a modular AI system
- Personality: Calm, precise, intelligent, humanlike

"""


#ANCHOR - Initialize base messages list
system_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

#ANCHOR - Chat log path
CHAT_LOG_PATH = os.path.join("Data", "Chatlog.json")

#ANCHOR - Load or initialize chat log
def load_chatlog():
    if not os.path.exists("Data"):
        os.makedirs("Data")
    if os.path.isfile(CHAT_LOG_PATH):
        with open(CHAT_LOG_PATH, "r") as f:
            return load(f)
    with open(CHAT_LOG_PATH, "w") as f:
        dump([], f)
    return []

def save_chatlog(log):
    with open(CHAT_LOG_PATH, "w") as f:
        dump(log, f, indent=4)

#ANCHOR - Get current date and time

def get_realtime_info():
    now = datetime.now()
    return f"""Please use this realtime information if needed:
Day: {now.strftime('%A')}
Date: {now.strftime('%d')}
Month: {now.strftime('%B')}
Year: {now.strftime('%Y')}
Time: {now.strftime('%H')} hours | {now.strftime('%M')} minutes | {now.strftime('%S')} seconds
"""

#ANCHOR - Clean up assistant's answer

def format_answer(answer):
    lines = [line.strip() for line in answer.split('\n') if line.strip()]
    return '\n'.join(lines)

#ANCHOR - Main chatbot function

def Chat(query):
    try:
        chatlog = load_chatlog()
        chatlog.append({"role": "user", "content": query})

        # Compose messages with system prompt + realtime info + history
        full_messages = system_messages + [{"role": "system", "content": get_realtime_info()}] + chatlog

        # Request to Groq API
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=full_messages,
            max_tokens=1024,
            temperature=1.0,
            top_p=1,
            stream=True
        )

        response = ""
        for chunk in completion:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
                response += delta

        print("\n")
        response = response.replace("</s>", "")
        chatlog.append({"role": "assistant", "content": response})
        save_chatlog(chatlog)

        return format_answer(response)

    except Exception as e:
        print(f"[ERROR] {e}")
        return "Something went wrong. Try again."


