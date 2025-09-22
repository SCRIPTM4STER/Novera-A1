# utils.py
# SECTION - Importing necessary libraries
from groq import Groq
from json import load, dump
from datetime import datetime
from dotenv import dotenv_values
import os

# SECTION - Load environment variables
env_vars = dotenv_values(".env")
USERNAME = env_vars.get("Username", "User")
GROQ_API_KEY = env_vars.get("GroqAPIKey")

# SECTION - Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)



# SECTION - Chat log path
CHAT_LOG_PATH = os.path.join("Data", "Chatlog.json")

# SECTION - Load or initialize chat log
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

# SECTION - Get current date and time
def get_realtime_info():
    now = datetime.now()
    return f"""Please use this realtime information if needed:
Day: {now.strftime('%A')}
Date: {now.strftime('%d')}
Month: {now.strftime('%B')}
Year: {now.strftime('%Y')}
Time: {now.strftime('%H')} hours | {now.strftime('%M')} minutes | {now.strftime('%S')} seconds
"""

# SECTION - Clean up assistant's answer
def format_answer(answer):
    lines = [line.strip() for line in answer.split('\n') if line.strip()]
    return '\n'.join(lines)
