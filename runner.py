# Central entry point. Receives parsed task types from core/router.py and calls the right submodule.
# Note: This file is not used in the project.(Right now)
import sys
import os
import logging

# Add the current directory to the path to ensure we import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from core.decision__Core import FirstLayerDMM
from core.router import Task__Router
from engine.Config.config import CONFIG, FN_KEYWORDS, COMMAND_TYPES
from engine.llm.LLMClient import LLMClient
from engine.controle__unit.controller import PortalManager

# Logger
logger = logging.getLogger(__name__)

# Initialize LLM client once
client = LLMClient(CONFIG)

# Initialize PortalManager once
Portal = PortalManager()
def setup(query):
    decisions = FirstLayerDMM(query)
    print(decisions)
    if not decisions:
        print("error")
        return
    # Route directly when there are 1 or 2 decisions
    if len(decisions) <= 2:
        router = Task__Router(decisions, FN_KEYWORDS, COMMAND_TYPES)
        tasks, _ = router.Parse_Classify_Tasks()

        # Execute per-task actions
        for task in tasks:
            task_type = task.get("type")
            fn = task.get("fn", "")
            payload = task.get("task", "")

            if task_type == "llm":
                try:
                    response = client.generate(prompt=payload)
                    print("LLM Response:", response)
                    logger.info("LLM response generated successfully")
                except Exception as e:
                    logger.error(f"Error generating LLM response: {e}")
                    print("Error: Could not generate response. Please try again.")
            elif task_type in ("app_control", "search"):
                # Let PortalManager interpret and execute the intent
                Portal.handle_query(f"{fn} {payload}")
            # Other types (generation/system/reminder) print from handlers

        # Keep legacy router result signal
        result = router.router()
        if result:
            print(result)
        return

    # More than 2: assign lettered variables and route each individually
    decisions_map = {}
    for i, decision in enumerate(decisions):
        var_name = chr(97 + i)  # 'a', 'b', 'c', ...
        decisions_map[var_name] = decision

    for var_name, single_decision in decisions_map.items():
        router = Task__Router([single_decision], FN_KEYWORDS, COMMAND_TYPES)
        tasks, _ = router.Parse_Classify_Tasks()

        for task in tasks:
            task_type = task.get("type")
            fn = task.get("fn", "")
            payload = task.get("task", "")

            if task_type == "llm":
                try:
                    response = client.generate(prompt=payload)
                    print(f"{var_name} (LLM) Response:", response)
                    logger.info("LLM response generated successfully")
                except Exception as e:
                    logger.error(f"Error generating LLM response: {e}")
                    print(f"{var_name} Error: Could not generate response.")
            elif task_type in ("app_control", "search"):
                Portal.handle_query(f"{fn} {payload}")
            elif task_type == "media":
                print("media")
            elif task_type == "generation":
                print("generation")
            elif task_type == "scheduler":
                print("scheduler")

        result = router.router()
        if result:
            print(f"{var_name} ->", result)

if __name__ == "__main__":
    while True:
                try:
                    query = input("user >>> ").strip()
                    if not query:
                        continue
                    setup(query=query)
                except Exception as e:
                    print(e)