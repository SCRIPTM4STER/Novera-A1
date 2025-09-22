# Client__loader.py
from groq import Groq
import cohere
try:
    import openai
except ImportError:
    openai = None

# Registry mapping LLM names -> initialization functions
CLIENT_REGISTRY = {
    "groq": lambda api_key: Groq(api_key=api_key),
    "cohere": lambda api_key: cohere.Client(api_key=api_key),
}

# Only add OpenAI if the module is installed
if openai is not None:
    CLIENT_REGISTRY["openai"] = lambda api_key: openai.OpenAI(api_key=api_key)
