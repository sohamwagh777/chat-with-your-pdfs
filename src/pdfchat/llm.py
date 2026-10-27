"""Chat completions via local Ollama."""
import requests

from .config import OLLAMA_URL, CHAT_MODEL


def chat(messages, model: str | None = None, temperature: float = 0.2) -> str:
    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model or CHAT_MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        },
        timeout=300,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]
