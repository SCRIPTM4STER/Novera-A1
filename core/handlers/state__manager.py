# state_manager.py
"""
This script may have some issues as it was made by AI. if possible fix this. and plese care to explain it I dont understand a word
P.S. currently not in use.
"""

class StateManager:
    def __init__(self):
        self.task_log = []
        self.short_term_memory = []

    def track(self, task, state):
        entry = {
            "fn": task.get("fn"),
            "task": task.get("task"),
            "type": task.get("type"),
            "state": state
        }
        self.task_log.append(entry)
        self.short_term_memory.append(entry)
        return entry

    def update_state(self, task, new_state):
        for log in self.task_log:
            if log["task"] == task["task"] and log["fn"] == task["fn"]:
                log["state"] = new_state
                return log
        return None

    def get_memory(self):
        return self.short_term_memory[-10:]  # Keep last 10 for short-term memory

    def clear_memory(self):
        self.short_term_memory = []
