# utils.py

# SECTION - Importing necessary libraries
from json import load, dump, JSONDecodeError
from datetime import datetime
from dotenv import dotenv_values
import os
from engine.Config.config import CONFIG
from engine.Config.logger import configure_logger

# SECTION - Load environment variables
env_vars = dotenv_values(".env")
USERNAME = env_vars.get("Username", "User")
GROQ_API_KEY = env_vars.get("GroqAPIKey")

# Resolve history config from CONFIG
_llm_cfg = CONFIG["LLM"][0]
_history_cfg = _llm_cfg.get("history", {})
CHAT_LOG_PATH = _history_cfg.get("path", os.path.join("Data", "Chatlog.json"))
HISTORY_LIMIT = int(_history_cfg.get("limit", 35))

# Logger configured based on CONFIG.logging
_logging_cfg = _llm_cfg.get("logging", {"enabled": False})
logger = configure_logger(_logging_cfg)


def load_history():
    """Load chat history from JSON file, create it if missing."""
    base_dir = os.path.dirname(os.path.abspath(CHAT_LOG_PATH)) or "Data"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    if os.path.isfile(CHAT_LOG_PATH):
        with open(CHAT_LOG_PATH, "r") as f:
            try:
                return load(f)
            except JSONDecodeError:
                # Recover from empty or malformed file by resetting to []
                with open(CHAT_LOG_PATH, "w") as wf:
                    dump([], wf)
                return []

    with open(CHAT_LOG_PATH, "w") as f:
        dump([], f)

    return []


def append_history(query: str, response: str):
    """Append a new chat entry and persist it."""
    history = load_history()
    history.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "user": USERNAME,
        "query": query,
        "response": response,
    })
    save_history(history)
    if _logging_cfg.get("enabled", False):
        try:
            logger.info(f"History appended; size={len(history)}")
        except Exception:
            pass


def format_recent_history(limit: int = None) -> str:
    """Return recent chat history as a readable string for LLM context."""
    history = load_history()
    effective_limit = limit if isinstance(limit, int) and limit > 0 else HISTORY_LIMIT
    recent = history[-effective_limit:] if len(history) > effective_limit else history
    # Create a lightweight textual transcript
    lines = []
    for item in recent:
        user = item.get("user", "User")
        q = item.get("query", "")
        r = item.get("response", "")
        if q:
            lines.append(f"{user}: {q}")
        if r:
            lines.append(f"Assistant: {r}")
    return "\n".join(lines)


def save_history(log):
    """Save chat history back to JSON file."""
    with open(CHAT_LOG_PATH, "w") as f:
        dump(log, f, indent=4)

def reset_history(query: str):
    if query == "reset":
        with open(CHAT_LOG_PATH, "w") as f:
            dump([], f)
        if _logging_cfg.get("enabled", False):
            try:
                logger.warning("Chat history reset via command")
            except Exception:
                pass