from core.decision__Core import FirsLayerDMM
from core.router import Task__Router
# from engine.llm.openrouterLLM import Chat
from engine.llm.groqLLM import Chat



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


if __name__ == '__main__':
    while True:
        query = input("user >>> ").strip()
        if not query:
            continue

        # First-level decision
        decisions = FirsLayerDMM(query)

        # Task classification
        router = Task__Router(decisions, fn_keywords, command_types)
        tasks, _ = router.Parse_Classify_Tasks()


        # Route the task(s)
        result = router.router()

        # Handle LLM output
        if result == "sent to LLM":
            QueryFinal = query.replace("general ", "").replace("realtime ", "").strip()
            # Clean query if needed
            response = Chat(query=QueryFinal)
            print(f"LLM >>> {response}")
        elif query.lower() == "exit":
            exit()
