from typing import Dict
from .Client__loader import CLIENT_REGISTRY

class LLMClient:
    def __init__(self, config: Dict):
        self.config = config
        self.llm = self.config["LLM"][0]["function"]

        self.name = self.llm["name"]  # groq, cohere, openai
        self.api_key = self.llm["parameters"]["api_key"]
        self.model = self.llm["parameters"]["model"]
        self.system_prompt = self.llm["parameters"]["system_prompt"]

        # Validate client
        if self.name not in CLIENT_REGISTRY:
            raise ValueError(f"Unknown LLM provider: {self.name}")

        # Initialize client
        self.client = CLIENT_REGISTRY[self.name](self.api_key)

    def generate(self, prompt: str) -> str:
        if not prompt:
            return "Error: prompt is empty"

        try:
            if self.name == "groq":
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                )
                # Groq: safe content extraction
                message_obj = resp.choices[0].message if resp.choices else None
                if message_obj is None:
                    return ""
                # Groq SDK sometimes returns dict, sometimes object
                if isinstance(message_obj, dict):
                    return message_obj.get("content", "")
                else:
                    return getattr(message_obj, "content", "")

            elif self.name == "cohere":
                resp = self.client.generate(
                    model=self.model,
                    prompt=f"{self.system_prompt}\nUser: {prompt}"
                )
                return getattr(resp.generations[0], "text", "") if resp.generations else ""

            elif self.name == "openai":
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
                message_obj = resp.choices[0].message if resp.choices else None
                return getattr(message_obj, "content", "") if message_obj else ""

            else:
                return f"Error: Unknown LLM {self.name}"

        except Exception as e:
            return f"Exception in generate(): {str(e)}"
