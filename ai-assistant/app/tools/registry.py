import json


class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, func, name: str = None, description: str = "", parameters: dict = None):
        n = name or func.__name__
        self._tools[n] = {
            "callable": func,
            "definition": {
                "type": "function",
                "function": {
                    "name": n,
                    "description": description,
                    "parameters": parameters or {"type": "object", "properties": {}},
                },
            },
        }

    def get_definitions(self):
        return [t["definition"] for t in self._tools.values()]

    def execute(self, name: str, args: dict):
        tool = self._tools.get(name)
        if not tool:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            result = tool["callable"](**args)
            return str(result)
        except Exception as e:
            return json.dumps({"error": str(e)})
