"""
Task orchestrator
"""
import re
import handlers.task__handler as exec_handlers

# copy and paste these in the main file 
# Recognized function keywords
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

# Task priority levels
command_priorities = {
    "llm": "Moderate",
    "app_control": "High",
    "media": "Low",
    "generation": "Moderate",
    "scheduler": "High",
    "system": "Critical",
    "search": "Minimal",
    "exit": "Critical"
}

class Task__Router:
    def __init__(self, decisions, fn_keywords, command_types):
        self.decisions = decisions
        self.fn_keywords = fn_keywords
        self.command_types = command_types

    def Parse_Classify_Tasks(self):
        self.tasks = []
        for decision in self.decisions:
            for fn in self.fn_keywords:
                match = re.search(rf"\b{re.escape(fn)}\b", decision, re.IGNORECASE)
                if match:
                    fn_word = match.group()
                    rest = decision.replace(fn_word, "", 1).strip()

                    task_type = None
                    for type_name, fn_list in self.command_types.items():
                        if fn_word in fn_list:
                            task_type = type_name
                            break

                    self.tasks.append({
                        "fn": fn_word,
                        "task": rest,
                        "type": task_type
                    })
                    break
        return self.tasks, None  # You could return task_type if needed

    def set__priority(self, tasks):
        self.prioritized = []
        for task in tasks:
            priority = command_priorities.get(task["type"], "Minimal")
            self.prioritized.append({
                "task": task["task"],
                "type": task["type"],
                "priority": priority
            })
        return self.prioritized

    def router(self):
        for task in self.tasks:
            task_type = task["type"]
            
            try:
                match task_type:
                    case "llm":
                        exec_handlers.handle_llm(task)
                    case "app_control":
                        exec_handlers.handle_app_control(task)
                    case "media":
                        exec_handlers.handle_app_control(task)
                    case "generation":
                        exec_handlers.handle_generation(task)
                    case "scheduler":
                        exec_handlers.handle_reminder(task)
                    case "system":
                        exec_handlers.handle_system(task)
                    case "search":
                        exec_handlers.handle_search(task)
                    case "exit":
                        exec_handlers.handle_exit(task)
                    case _:
                        print("[Router] Unknown task type.")
            except Exception as e:
                print(f"[Router Error] Task failed: {e}")

#=== Test Run ===#
sample_input = ["open camera", "generate image of cat"]              
router = Task__Router(sample_input, fn_keywords, command_types)

tasks, _ = router.Parse_Classify_Tasks()
prioritized_output = router.set__priority(tasks=tasks)
router.router()

print("Parsed Tasks:", tasks)
print("Prioritized__Tasks:", prioritized_output)
