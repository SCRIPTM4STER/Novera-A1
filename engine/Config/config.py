from .instructions import SYSTEM_PROMPT
from dotenv import dotenv_values
import os
import sys

def validate_env():
    """Validate required environment variables with clear error messages"""
    env_file = ".env"
    
    # Check if .env file exists
    if not os.path.exists(env_file):
        print("❌ Error: .env file not found!")
        print("📝 Please create a .env file based on .env.example")
        print("💡 Copy .env.example to .env and fill in your API keys")
        sys.exit(1)
    
    env_vars = dotenv_values(env_file)
    missing_vars = []
    
    # Check required variables
    required_vars = {
        "CohereAPIKey": "Cohere API key (required for decision making)",
        "GroqAPIKey": "Groq API key (required for LLM responses)"
    }
    
    for var, description in required_vars.items():
        value = env_vars.get(var)
        if not value or value.strip() == "":
            missing_vars.append(f"  • {var}: {description}")
    
    if missing_vars:
        print("❌ Error: Missing required environment variables!")
        print("📝 Please add the following to your .env file:")
        for var in missing_vars:
            print(var)
        print("\n💡 Get your API keys from:")
        print("  • Cohere: https://cohere.ai/")
        print("  • Groq: https://groq.com/")
        sys.exit(1)
    
    print("✅ Environment variables validated successfully")
    return env_vars

# Validate environment on import
env_vars = validate_env()
GROQ_API_KEY = env_vars.get("GroqAPIKey")

# Centralized command schema to prevent drift between modules
FN_KEYWORDS = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", 
]

COMMAND_TYPES = {
    "llm": ["general", "realtime"],
    "app_control": ["open", "close"],
    "media": ["play"],
    "generation": ["generate image", "content"],
    "scheduler": ["reminder"],
    "system": ["system"],
    "search": ["google search", "youtube search"],
    "exit": ["exit"],
}

CONFIG = {
    "LLM": [
        {
            "type": "LLM",
            "function": {
                "name": "groq",  # swap "cohere" or "openai"
                "description": "A simple test",
                "parameters": {
                    "api_key": GROQ_API_KEY,
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "system_prompt": SYSTEM_PROMPT,  # make sure this exists
                },
            },
            "history": {
                "limit": 35,
                "path": "Data/Chatlog.json",
            },
            "behavior": {
                "tone": "friendly",
                "verbosity": "medium",
                "use_emojis": False
            },
            "context": {
                "use_short_term_memory": True,
                "short_term_limit": 5,  # last 5 messages
                "use_long_term_memory": False,
                "long_term_path": "Data/LongTermMemory.json"
            },
            "logging": {
                "enabled": True,
                "log_path": "Data/AI_debug.log",
                "level": "INFO"  # options: DEBUG, INFO, WARNING, ERROR
            },
            "personalization": {
                "user_profile": {
                    "name": "User",
                    "nickname": "User",
                    "preferred_name": "Emberbane",
                    "more_about_you": "None",
                    "interests": ["tech", "fantasy novels", "gaming"],
                    "language": "en",
                    "timezone": "Asia/Dhaka",
                    "reference_chat_history": True,
                    "save_history": True
                },
            },
        }
    ]
}
