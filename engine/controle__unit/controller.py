from webbrowser import open as web__opener
import cohere
from dotenv import dotenv_values
import ast
import subprocess
import sys

# Load environment variables
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")
if not CohereAPIKey:
    raise ValueError("Cohere API key is missing! Please check your .env file.")

# Create Cohere client
co = cohere.Client(api_key=CohereAPIKey)

# Chat settings
messages = []
preamble = """
You are an extremely precise App+Web Control model.
Your only job is to output a Python dictionary in the format:
{"apps": ["app1", "app2"], "urls": ["https://site1.com/", "https://site2.com/"]}
Only include valid executable app names and fully qualified URLs.
Do not add any explanations or text outside the dictionary.
"""

ChatHistory = [
    {"role": "User", "message": "open youtube"},
    {"role": "Chatbot", "message": "{\"apps\": [], \"urls\": [\"https://www.youtube.com/\"]}"},
    {"role": "User", "message": "open facebook and notepad"},
    {"role": "Chatbot", "message": "{\"apps\": [\"notepad\"], \"urls\": [\"https://www.facebook.com/\"]}"},
]

class PortalManager:

    def __init__(self):
        self.chat_history = ChatHistory

    def _launch_app(self, app_name: str):
        """Open system applications cross-platform"""
        try:
            if sys.platform.startswith("win"):
                subprocess.Popen(["start", "", app_name], shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                subprocess.Popen([app_name])
        except Exception as e:
            print(f"Error launching {app_name}: {e}")

    def _launch_url(self, url: str):
        """Open URLs in default browser"""
        try:
            web__opener(url)
        except Exception as e:
            print(f"Error opening URL {url}: {e}")

    def handle_query(self, query: str):
        """Main method to parse query and execute commands"""
        messages.append({"role": "user", "content": query})
        self.chat_history.append({"role": "User", "message": query})

        # Get structured output from Cohere
        stream = co.chat_stream(
            model='command-r-plus',
            message=query,
            temperature=0,
            chat_history=self.chat_history,
            prompt_truncation='OFF',
            connectors=[],
            preamble=preamble,
        )

        response = ""
        for event in stream:
            if event.event_type == "text-generation":
                response += event.text

        # Parse the JSON-like dictionary safely
        try:
            parsed = ast.literal_eval(response.strip())
        except Exception as e:
            print(f"Error parsing model output: {e}")
            return

        # Open apps
        SAFE_APPS = [
            # Browsers
            "chrome", "google chrome", "firefox", "mozilla firefox",
            "edge", "msedge", "microsoft edge", "brave", "opera",

            # Text editors
            "notepad", "wordpad", "sublime_text", "vscode", "code", "notepad++",

            # Office / productivity
            "excel", "word", "powerpoint", "onenote",

            # Communication
            "discord", "slack", "zoom", "teams", "skype",

            # Media players
            "vlc", "windows media player", "spotify",

            # System tools
            "calc", "calculator", "cmd", "powershell",
        ]

        for app in parsed.get("apps", []):
            if app.strip().lower() in SAFE_APPS:
                self._launch_app(app.strip())
            else:
                print(f"Blocked unsafe app: {app}")


        # Open URLs
        for url in parsed.get("urls", []):
            if isinstance(url, str) and url.strip().startswith("http"):
                self._launch_url(url.strip())


# Example usage
if __name__ == "__main__":
    Portal = PortalManager()
    Portal.handle_query("can u launch chrome?")
