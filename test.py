from core.decision__Core import FirsLayerDMM
from core.task__orchestrator import Task__Router


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

#*NOTE - exicute the script
if __name__ == '__main__':
    #* Use a while loop to continuously prompt the user for input
    while True:
        userInput = input("user >>> ") 
        decisions = FirsLayerDMM(userInput)
        router = Task__Router(decisions, fn_keywords, command_types)
        output, _ = router.Parse_Classify_Tasks()
        value = router.set__priority(tasks=output)
        distributor = router.router()
        print(value)
        print(router)