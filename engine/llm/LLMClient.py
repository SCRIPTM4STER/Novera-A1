from typing import Dict
from .Client__loader import CLIENT_REGISTRY
from .utils import format_recent_history, append_history
from engine.Config.logger import configure_logger
class LLMClient:
    def __init__(self, config: Dict):
        self.config = config
        self.cfg_root = self.config["LLM"][0]
        self.llm = self.cfg_root["function"]

        # Provider & model
        self.name = self.llm["name"]  # groq, cohere, openai
        params = self.llm["parameters"]
        self.api_key = self.llm["parameters"]["api_key"]
        self.model = self.llm["parameters"]["model"]
        self.system_prompt = params["system_prompt"]

        # Logging
        self.logging_cfg = self.cfg_root.get("logging", {"enabled": False})
        self.logger = configure_logger(self.logging_cfg)

        # History & context
        hist_cfg = self.cfg_root.get("history", {})
        self.history_limit = int(hist_cfg.get("limit", 35))

        ctx_cfg = self.cfg_root.get("context", {})
        self.use_stm = bool(ctx_cfg.get("use_short_term_memory", True))
        self.stm_limit = int(ctx_cfg.get("short_term_limit", 5))
        self.use_ltm = bool(ctx_cfg.get("use_long_term_memory", False))
        self.ltm_path = ctx_cfg.get("long_term_path", "Data/LongTermMemory.json")

        # Personalization
        pers = self.cfg_root.get("personalization", {}).get("user_profile", {})
        self.user_name = pers.get("name", "User")
        self.user_nickname = pers.get("nickname", self.user_name)
        self.preferred_name = pers.get("preferred_name", self.user_name)
        self.more_about_user = pers.get("more_about_you", "")
        self.interests = pers.get("interests", [])
        self.language = pers.get("language", "en")
        self.timezone = pers.get("timezone", "UTC")
        self.reference_chat_history = bool(pers.get("reference_chat_history", True))
        self.save_history_flag = bool(pers.get("save_history", True))
        # Validate client
        if self.name not in CLIENT_REGISTRY:
            raise ValueError(f"Unknown LLM provider: {self.name}")

        # Initialize client
        self.client = CLIENT_REGISTRY[self.name](self.api_key)

    def generate(self, prompt: str) -> str:
        if not prompt:
            return "Error: prompt is empty"

        # Preserve original user prompt for history
        original_user_prompt = prompt

        # Build context with recent conversation (respect STM settings)
        transcript = ""
        if self.reference_chat_history and self.use_stm:
            try:
                transcript = format_recent_history(limit=self.stm_limit)
            except Exception as e:
                if self.logging_cfg.get("enabled", False):
                    try:
                        self.logger.warning(f"History formatting failed: {e}")
                    except Exception:
                        pass
                transcript = ""
        # For chat-based providers we will pass system prompt separately,
        # so user message should not repeat system prompt.
        user_message = f"{transcript}\nUser: {original_user_prompt}" if transcript else original_user_prompt

        try:
            if self.name == "groq":
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
                        {"role": "user", "content": user_message},
                    ],
                )
                # Groq: safe content extraction
                message_obj = resp.choices[0].message if resp.choices else None
                if message_obj is None:
                    return ""
                # Groq SDK sometimes returns dict, sometimes object
                if isinstance(message_obj, dict):
                    content = message_obj.get("content", "")
                else:
                    content = getattr(message_obj, "content", "")

                # Persist history
                if self.save_history_flag:
                    append_history(original_user_prompt, content)
                if self.logging_cfg.get("enabled", False):
                    try:
                        self.logger.info("LLM[groq] call ok")
                    except Exception:
                        pass
                return content

            elif self.name == "cohere":
                resp = self.client.generate(
                    model=self.model,
                    prompt=f"{self.system_prompt}\n{user_message}"
                )
                content = getattr(resp.generations[0], "text", "") if resp.generations else ""
                if self.save_history_flag:
                    append_history(original_user_prompt, content)
                if self.logging_cfg.get("enabled", False):
                    try:
                        self.logger.info("LLM[cohere] call ok")
                    except Exception:
                        pass
                return content

            elif self.name == "openai":
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.7,
                )
                message_obj = resp.choices[0].message if resp.choices else None
                content = getattr(message_obj, "content", "") if message_obj else ""
                if self.save_history_flag:
                    append_history(original_user_prompt, content)
                if self.logging_cfg.get("enabled", False):
                    try:
                        self.logger.info("LLM[openai] call ok")
                    except Exception:
                        pass
                return content

            else:
                return f"Error: Unknown LLM {self.name}"

        except Exception as e:
            if self.logging_cfg.get("enabled", False):
                try:
                    self.logger.error(f"LLM generate() error: {e}")
                except Exception:
                    pass
            return f"Exception in generate(): {str(e)}"
