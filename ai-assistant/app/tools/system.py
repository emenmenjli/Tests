import subprocess
import json
from pathlib import Path


def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"File not found: {path}"
    return p.read_text(encoding="utf-8", errors="replace")


def write_file(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Written to {path}"


def list_files(path: str = ".") -> str:
    p = Path(path)
    if not p.exists():
        return f"Path not found: {path}"
    items = []
    for child in p.iterdir():
        items.append(f"{'[DIR]' if child.is_dir() else '[FILE]'} {child.name}")
    return "\n".join(items) if items else "(empty)"


def run_command(command: str) -> str:
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr or "(no output)"
        return output[:3000]
    except subprocess.TimeoutExpired:
        return "Command timed out (30s)"
    except Exception as e:
        return f"Error: {e}"


SYSTEM_TOOLS = [
    (read_file, "read_file", "Read a file from the filesystem", {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Absolute or relative path to the file"}
        },
        "required": ["path"],
    }),
    (write_file, "write_file", "Write content to a file (overwrites existing)", {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to the file"},
            "content": {"type": "string", "description": "Content to write"},
        },
        "required": ["path", "content"],
    }),
    (list_files, "list_files", "List files in a directory", {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path (default: current)"},
        },
    }),
    (run_command, "run_command", "Run a shell command and return output", {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"},
        },
        "required": ["command"],
    }),
]
