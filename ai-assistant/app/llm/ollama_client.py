import json
import requests
from app.config import Config


class OllamaClient:
    def __init__(self):
        self.base_url = Config.OLLAMA_URL.rstrip("/")
        self.model = Config.OLLAMA_MODEL

    def chat(self, messages: list, tools: list = None):
        payload = {"model": self.model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["function"]["name"],
                        "description": t["function"].get("description", ""),
                        "parameters": t["function"]["parameters"],
                    },
                }
                for t in tools
            ]
        resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        msg = data.get("message", {})
        result = {"role": "assistant", "content": msg.get("content", "")}
        if "tool_calls" in msg:
            result["tool_calls"] = [
                {
                    "id": tc.get("function", {}).get("name", "unknown"),
                    "type": "function",
                    "function": {
                        "name": tc["function"]["name"],
                        "arguments": json.dumps(tc["function"]["arguments"]),
                    },
                }
                for tc in msg["tool_calls"]
            ]
        return result

    def name(self):
        return f"Ollama ({self.model})"
