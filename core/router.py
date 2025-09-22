"""
Task orchestrator
"""
import re
from .handlers import task__handler as exec_handlers

# copy and paste these in the main file 
# Recognized function keywords
""" 
fn_keywords = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder", 
]

# Command type classification
command_types = {
    "llm": ["general", "realtime"],
    "app_control": ["open", "close"],
    "media": ["play"],
    "generation": ["generate image", "content"],
    "scheduler": ["reminder"],
    "system": ["system"],
    "search": ["google search", "youtube search"],
    "exit": ["exit"],
}
"""



class Task__Router:
    def __init__(self, decisions, fn_keywords, command_types):
        self.decisions = decisions
        self.fn_keywords = fn_keywords
        self.command_types = command_types

        # Precompiled patterns
        self.fn_patterns = [(kw, re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)) for kw in fn_keywords]

        # Task type to handler class map
        self.handler_map = {
            "llm": exec_handlers.LLMHandler,
            "app_control": exec_handlers.AppControlHandler,
            "media": exec_handlers.AppControlHandler,
            "generation": exec_handlers.GenerationHandler,
            "scheduler": exec_handlers.ReminderHandler,
            "system": exec_handlers.SystemHandler,
            "search": exec_handlers.SearchHandler,
        }

    def Parse_Classify_Tasks(self):
        self.tasks = []
        for decision in self.decisions:
            for fn, pattern in self.fn_patterns:
                if pattern.search(decision):
                    rest = pattern.sub("", decision, count=1).strip()

                    task_type = next(
                        (type_name for type_name, fn_list in self.command_types.items() if fn in fn_list),
                        None
                    )

                    self.tasks.append({
                        "fn": fn,
                        "task": rest,
                        "type": task_type
                    })
                    break  # Only match the first valid keyword
        return self.tasks, None

    def router(self):
        for task in self.tasks:
            task_type = task["type"]
            handler_cls = self.handler_map.get(task_type)

            if not handler_cls:
                print("[Router] Unknown task type.")
                continue


            try:
                handler = handler_cls()
                result = handler.handle(task)
                if task_type == "llm" and getattr(handler, "LLM", False):
                    return "Is LLM"
                elif task == "app_control" and getattr(handler, "App Control", False):
                    return "Is App Control"

            except Exception as e:
                print(f"[Router Error] Task failed: {e}") 