from webbrowser import open as web__opener
import cohere
from dotenv import dotenv_values
import ast
import subprocess
import sys
import os
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Load environment variables (validated in config)
from engine.Config.config import validate_env
env_vars = validate_env()
CohereAPIKey = env_vars.get("CohereAPIKey")

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
        """Open system applications cross-platform with improved safety"""
        try:
            # Validate app name (basic security check)
            if not app_name or len(app_name.strip()) == 0:
                logger.warning("Empty app name provided")
                return False
                
            app_name = app_name.strip()
            
            # Check for potentially dangerous characters
            dangerous_chars = ['&', '|', ';', '`', '$', '(', ')', '<', '>', '"', "'"]
            if any(char in app_name for char in dangerous_chars):
                logger.warning(f"Potentially dangerous characters in app name: {app_name}")
                return False
            
            if sys.platform.startswith("win"):
                # Use os.startfile for Windows (safer than shell=True)
                try:
                    os.startfile(app_name)
                    logger.info(f"Successfully launched app: {app_name}")
                    return True
                except OSError:
                    # Fallback to subprocess without shell
                    subprocess.Popen([app_name], shell=False)
                    logger.info(f"Successfully launched app via subprocess: {app_name}")
                    return True
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", app_name], shell=False)
                logger.info(f"Successfully launched app on macOS: {app_name}")
                return True
            else:
                subprocess.Popen([app_name], shell=False)
                logger.info(f"Successfully launched app on Linux: {app_name}")
                return True
        except Exception as e:
            logger.error(f"Error launching {app_name}: {e}")
            print(f"Error launching {app_name}: {e}")
            return False

    def _launch_url(self, url: str):
        """Open URLs in default browser with validation"""
        try:
            # Validate URL format
            if not url or len(url.strip()) == 0:
                logger.warning("Empty URL provided")
                return False
                
            url = url.strip()
            
            # Parse URL to validate format
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                logger.warning(f"Invalid URL format: {url}")
                return False
                
            # Only allow http and https schemes
            if parsed.scheme not in ['http', 'https']:
                logger.warning(f"Unsafe URL scheme: {parsed.scheme}")
                return False
                
            # Basic domain validation (prevent localhost abuse)
            if parsed.netloc in ['localhost', '127.0.0.1', '0.0.0.0']:
                logger.warning(f"Blocked localhost URL: {url}")
                return False
                
            web__opener(url)
            logger.info(f"Successfully opened URL: {url}")
            return True
        except Exception as e:
            logger.error(f"Error opening URL {url}: {e}")
            print(f"Error opening URL {url}: {e}")
            return False

    def handle_query(self, query: str):
        """Main method to parse query and execute commands"""
        messages.append({"role": "user", "content": query})
        self.chat_history.append({"role": "User", "message": query})

        # Get structured output from Cohere
        stream = co.chat_stream(
            model='command-a-03-2025',
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

        # Launch apps with improved safety
        for app in parsed.get("apps", []):
            if isinstance(app, str) and app.strip().lower() in SAFE_APPS:
                success = self._launch_app(app.strip())
                if not success:
                    print(f"Failed to launch app: {app}")
            else:
                logger.warning(f"Blocked unsafe app: {app}")
                print(f"Blocked unsafe app: {app}")

        # Open URLs with validation
        for url in parsed.get("urls", []):
            if isinstance(url, str):
                success = self._launch_url(url.strip())
                if not success:
                    print(f"Failed to open URL: {url}")


# Example usage
# if __name__ == "__main__":
#     Portal = PortalManager()
#     Portal.handle_query("can u launch chrome?")
