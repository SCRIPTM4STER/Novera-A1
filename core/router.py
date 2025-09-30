"""
Task orchestrator
"""
import re
import logging
from .handlers import task__handler as exec_handlers

logger = logging.getLogger(__name__)

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
        if not self.tasks:
            logger.warning("No tasks to route")
            return None
            
        for task in self.tasks:
            task_type = task["type"]
            handler_cls = self.handler_map.get(task_type)

            if not handler_cls:
                logger.warning(f"Unknown task type: {task_type}")
                print(f"[Router] Unknown task type: {task_type}")
                continue

            try:
                handler = handler_cls()
                result = handler.handle(task) #is not used in the project(right now)
                logger.info(f"Task {task_type} handled successfully")
                
                if task_type == "llm" and getattr(handler, "LLM", False):
                    return "Is LLM"
                elif task_type == "app_control" and getattr(handler, "success", False):
                    return "Is App Control"
                elif task_type == "search" and getattr(handler, "success", False):
                    return "Is Web Search"
                elif task_type == "media" and getattr(handler, "success", False):
                    return "Is Media"
                elif task_type == "generation" and getattr(handler, "success", False):
                    return "Is Generation"
                elif task_type == "scheduler" and getattr(handler, "success", False):
                    return "Is Scheduler"
                

            except Exception as e:
                logger.error(f"Task {task_type} failed: {e}")
                print(f"[Router Error] Task {task_type} failed: {e}")
                continue
                
        return None
