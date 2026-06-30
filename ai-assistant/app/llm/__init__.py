from app.llm.openai_client import OpenAIClient
from app.llm.anthropic_client import AnthropicClient
from app.llm.ollama_client import OllamaClient
from app.config import Config


def get_llm():
    backend = Config.LLM_BACKEND.lower()
    if backend == "openai":
        return OpenAIClient()
    elif backend == "anthropic":
        return AnthropicClient()
    elif backend == "ollama":
        return OllamaClient()
    else:
        raise ValueError(f"Unknown LLM backend: {backend}")
