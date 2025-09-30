import sys
import os
import logging
# Add the current directory to the path to ensure we import local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.Config.config import CONFIG, FN_KEYWORDS, COMMAND_TYPES
from engine.Config.logger import configure_logger

# Configure logger based on CONFIG["LLM"][0]["logging"]
_logging_cfg = CONFIG["LLM"][0].get("logging", {"enabled": False})
logger = configure_logger(_logging_cfg)

from core.decision__Core import FirstLayerDMM
from core.router import Task__Router
from engine.llm import LLMClient
from engine.controle__unit.controller import PortalManager
from engine.llm.utils import append_history
# Initialize LLM client once
client = LLMClient.LLMClient(CONFIG)

# Initialize PortalManager once
Portal = PortalManager()

# Use centralized command schema from config

if __name__ == "__main__":
    try:
        print("Novera AI ready. Type 'exit' to quit.\n")
        logger.info("Novera AI system initialized successfully")

        while True:
            try:
                query = input("user >>> ").strip()
                if not query:
                    continue

                logger.info(f"Processing query: {query}")

                # Step 1: First-level decision (cohere classifier)
                try:
                    decisions = FirstLayerDMM(query)
                    logger.info(f"Decisions made: {decisions}")
                except Exception as e:
                    logger.error(f"Error in decision making: {e}")
                    print("Error: Could not process your request. Please try again.")
                    continue

                # Step 2: Task classification
                try:
                    router = Task__Router(decisions, FN_KEYWORDS, COMMAND_TYPES)
                    tasks, _ = router.Parse_Classify_Tasks()
                    logger.info(f"Tasks classified: {tasks}")
                except Exception as e:
                    logger.error(f"Error in task classification: {e}")
                    print("Error: Could not classify your request. Please try again.")
                    continue

                # Step 3: Route tasks
                try:
                    result = router.router()
                    logger.info(f"Router result: {result}")
                except Exception as e:
                    logger.error(f"Error in task routing: {e}")
                    print("Error: Could not route your request. Please try again.")
                    continue

                print("Decisions:", decisions)
                print("Router Result:", result)

                # Step 4: If router says it's an LLM task, send to client
                if result == "Is LLM":
                    for task in tasks:
                        if task["type"] == "llm":
                            try:
                                response = client.generate(prompt=task["task"])
                                print("LLM Response:", response)
                                # History persistence now handled by LLMClient
                                logger.info("LLM response generated successfully")
                                
                            except Exception as e:
                                logger.error(f"Error generating LLM response: {e}")
                                print("Error: Could not generate response. Please try again.")
                elif result == "Is App Control":
                    for task in tasks:
                        if task["type"] == "app_control":
                            try:
                                Portal.handle_query(task["task"])
                                logger.info("App control task executed successfully")
                            except Exception as e:
                                logger.error(f"Error in app control: {e}")
                                print("Error: Could not execute app control. Please try again.")
                else:
                    print("Task handled by router.")
                    logger.info("Task handled by router")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                logger.info("User interrupted with Ctrl+C")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                print("An unexpected error occurred. Please try again.")

    except Exception as e:
        logger.critical(f"Critical error during system initialization: {e}")
        print("Critical error: Could not initialize the system.")
        sys.exit(1)