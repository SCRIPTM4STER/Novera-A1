from core.decision__Core import FirsLayerDMM
from core.router import Task__Router
from engine.Config.config import CONFIG
from engine.llm import LLMClient


# Initialize LLM client once
client = LLMClient.LLMClient(CONFIG)

# Keywords and command types (copied from Task__Router docstring)
fn_keywords = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder",
]

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

if __name__ == "__main__":
    print("Novera AI ready. Type 'exit' to quit.\n")

    while True:
        query = input("user >>> ").strip()
        if not query:
            continue

        # Step 1: First-level decision (cohere classifier)
        decisions = FirsLayerDMM(query)

        # Step 2: Task classification
        router = Task__Router(decisions, fn_keywords, command_types)
        tasks, _ = router.Parse_Classify_Tasks()

        # Step 3: Route tasks
        result = router.router()

        print("Decisions:", decisions)
        print("Router Result:", result)

        # Step 4: If router says it's an LLM task, send to client
        if result == "Is LLM":
            for task in tasks:
                if task["type"] == "llm":
                    response = client.generate(prompt=task["task"])
                    print("LLM Response:", response)
                elif task["type"] == "app_control":
                    