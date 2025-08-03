# handlers.py

def handle_app_control(task):
    print(f"[AppHandler] Performing '{task['fn']}' on: {task['task']}")

def handle_reminder(task):
    print(f"[ReminderService] Scheduling reminder: {task['task']}")

def handle_generation(task):
    print(f"[ContentGenerator] Generating: {task['task']}")

def handle_llm(task):
    print(f"[LLMChat] Processing: {task['task']}")

def handle_search(task):
    print(f"[WebSearch] Searching for: {task['task']}")

def handle_system(task):
    print(f"[SystemManager] Executing system-level task: {task['task']}")

def handle_exit(task):
    print("[ExitHandler] Terminating task flow.")
 