"""
Free models from open router
deepseek-r1-distill-llama-70b:free
deepseek-r1-0528-qwen3-8b:free
qwen3-235b-a22b:free
"""

# Import necessary libraries
from json import load, dump
from datetime import datetime
from dotenv import dotenv_values
import os
import requests
import json

# Load environment variables from .env file
env_vars = dotenv_values(".env")

# Retrieve the environment variables for Username, Assistant name, and API key
USERNAME = env_vars.get("Username", "User")
ASSISTANT_NAME = env_vars.get("AssistantName", "Sophia")
API_KEY = env_vars.get("OpenRouterAPIkey")


# Define system prompt describing the assistant's behavior
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

# Initialize base messages list
system_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Chat log path
CHAT_LOG_PATH = os.path.join("Data", "Chatlog.json")

# Load or initialize chat log
def load__chatlog():
    if not os.path.exists("Data"):
        os.makedirs("Data")
    if os.path.isfile(CHAT_LOG_PATH):
        with open(CHAT_LOG_PATH, "r") as f:
            return load(f)
    with open(CHAT_LOG_PATH, "w") as f:
        dump([], f)
    return []

def save__chatlog(log):
    with open(CHAT_LOG_PATH, "w") as f:
        dump(log, f, indent=4)

# Get current date and time
def get_realtime_info():
    now = datetime.now()
    return f"""Please use this realtime information if needed:
    Day: {now.strftime('%A')}
    Date: {now.strftime('%d')}
    Month: {now.strftime('%B')}
    Year: {now.strftime('%Y')}
    Time: {now.strftime('%H')} hours | {now.strftime('%M')} minutes | {now.strftime('%S')} seconds
"""

# Clean up assistant's answer
def format__answer(answer):
    lines = [line.strip() for line in answer.split('\n') if line.strip()]
    return '\n'.join(lines)

def Chat(query, model):
    try:
        chatlog = load__chatlog()
        chatlog.append({"role": "user", "content": query})

        # Compose messages with system prompt + realtime info + history
        full_messages = system_messages + [{"role": "system", "content": get_realtime_info()}] + chatlog

        # Set up headers and data for OpenRouter API request
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": f"{model}",
            "messages": full_messages,
            "temperature": 1.0,
            "max_tokens": 1024,
            "stream": True
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            stream=True
        )

        if response.status_code != 200:
            return f"Error: {response.text}"

        response_text = ""
        for chunk in response.iter_lines():
            if chunk:
                line = chunk.decode("utf-8").strip()
                if line.startswith("data: "):
                    data_json = line[len("data: "):]
                    if data_json == "[DONE]":
                        break
                    try:
                        parsed = json.loads(data_json)
                        delta = parsed["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        # print(content, end="", flush=True)
                        response_text += content
                    except Exception as parse_error:
                        print(f"[CHUNK ERROR] {parse_error}")

        # Clean up the response
        cleaned_response = format__answer(response_text)

        # Update chat log with assistant response
        chatlog.append({"role": "assistant", "content": cleaned_response})
        save__chatlog(chatlog)

        return cleaned_response

    except Exception as e:
        print(f"[ERROR] {e}")
        return "Something went wrong. Try again."
