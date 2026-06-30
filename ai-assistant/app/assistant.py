import json
import threading
from app.memory import Memory
from app.llm import get_llm
from app.tools.registry import ToolRegistry
from app.tools.system import SYSTEM_TOOLS
from app.tools.email_tool import EMAIL_TOOLS
from app.tools.web import WEB_TOOLS


SYSTEM_PROMPT = """You are an AI desktop assistant with access to the user's computer and accounts.
You can read/write files, run commands, send emails, and search the web.
Be helpful, concise, and proactive. When running commands, be safe.
Use the tools provided to you when needed. If no tools are needed, just respond normally."""


class Assistant:
    def __init__(self):
        self.memory = Memory()
        self.llm = get_llm()
        self.tools = ToolRegistry()
        self._register_tools()

    def _register_tools(self):
        for func, name, desc, params in SYSTEM_TOOLS + EMAIL_TOOLS + WEB_TOOLS:
            self.tools.register(func, name=name, description=desc, parameters=params)

    def _parse_tool_call_json(self, text: str) -> list | None:
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "name" in data and "parameters" in data:
                return [{
                    "id": data["name"],
                    "type": "function",
                    "function": {"name": data["name"], "arguments": json.dumps(data["parameters"])},
                }]
        except (json.JSONDecodeError, TypeError):
            pass
        return None

    def process_message(self, user_msg: str, on_update=None):
        self.memory.add_message("user", user_msg)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.memory.get_recent())

        if on_update:
            on_update("assistant", "")

        while True:
            response = self.llm.chat(messages, tools=self.tools.get_definitions())
            tool_calls = response.get("tool_calls")
            content = response.get("content", "")

            if not tool_calls and content.strip():
                parsed = self._parse_tool_call_json(content)
                if parsed:
                    tool_calls = parsed
                    content = ""

            if not tool_calls:
                if content:
                    self.memory.add_message("assistant", content)
                if on_update:
                    on_update("assistant_complete", content)
                return content

            messages.append({"role": "assistant", "content": content})
            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}
                if on_update:
                    on_update("tool_start", f"{tool_name}({args})")

                result = self.tools.execute(tool_name, args)
                self.memory.add_tool_call(tool_name, args, result)

                if on_update:
                    on_update("tool_result", f"  -> {result[:200]}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id", tool_name),
                    "content": result,
                })

    def get_model_name(self):
        return self.llm.name()

    def clear_history(self):
        self.memory.clear()

    def switch_backend(self, backend: str):
        from app.config import Config
        Config.LLM_BACKEND = backend
        self.llm = get_llm()
