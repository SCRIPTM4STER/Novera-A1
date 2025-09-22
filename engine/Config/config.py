from .instructions import SYSTEM_PROMPT
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
GROQ_API_KEY = env_vars.get("GroqAPIKey")



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
                    "system_prompt": SYSTEM_PROMPT,
                },
            },
        }
    ]
}
