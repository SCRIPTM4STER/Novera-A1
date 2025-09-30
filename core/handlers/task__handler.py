# handlers.py

class AppControlHandler:
    def __init__(self):
        self.success = False

    def handle(self, task):
        self.success = True
        return self.success


class ReminderHandler:
    def __init__(self):
        self.success = False

    def handle(self, task):
        print(f"[ReminderService] Scheduling reminder: {task['task']}")
        self.success = True
        return self.success


class GenerationHandler:
    def __init__(self):
        self.success = False

    def handle(self, task):
        print(f"[ContentGenerator] Generating: {task['task']}")
        self.success = True
        return self.success


class LLMHandler:
    def __init__(self):
        self.LLM = False

    def handle(self, task):
        self.LLM = True
        return self.LLM


class SearchHandler:
    def __init__(self):
        self.success = False

    def handle(self, task):
        self.success = True
        return self.success


class SystemHandler:
    def __init__(self):
        self.success = False

    def handle(self, task):
        print(f"[SystemManager] Executing system-level task: {task['task']}")
        self.success = True
        return self.success


