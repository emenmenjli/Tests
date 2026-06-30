import json
from anthropic import Anthropic
from app.config import Config


class AnthropicClient:
    def __init__(self):
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL

    def chat(self, messages: list, tools: list = None):
        system_msg = None
        if messages and messages[0]["role"] == "system":
            system_msg = messages.pop(0)["content"]

        anthropic_messages = []
        for m in messages:
            if m["role"] == "tool":
                anthropic_messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": m["tool_call_id"],
                        "content": m["content"],
                    }],
                })
            else:
                anthropic_messages.append({"role": m["role"], "content": m["content"]})

        api_tools = None
        if tools:
            api_tools = []
            for t in tools:
                api_tools.append({
                    "name": t["function"]["name"],
                    "description": t["function"].get("description", ""),
                    "input_schema": t["function"]["parameters"],
                })

        kwargs = {"model": self.model, "max_tokens": 4096, "messages": anthropic_messages}
        if system_msg:
            kwargs["system"] = system_msg
        if api_tools:
            kwargs["tools"] = api_tools

        resp = self.client.messages.create(**kwargs)

        result = {"role": "assistant", "content": ""}
        tool_calls = []
        for block in resp.content:
            if block.type == "text":
                result["content"] = block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {"name": block.name, "arguments": json.dumps(block.input)},
                })
        if tool_calls:
            result["tool_calls"] = tool_calls

        if system_msg:
            messages.insert(0, {"role": "system", "content": system_msg})
        return result

    def name(self):
        return f"Anthropic ({self.model})"
