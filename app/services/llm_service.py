
import os

import httpx
from dotenv import load_dotenv


load_dotenv()

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_CHAT_MODEL = os.getenv(
    "OLLAMA_CHAT_MODEL",
    "llama3.2:latest",
)

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()


def generate_ai_response(messages: list[dict]) -> str:
    url = f"{OLLAMA_BASE_URL}/api/chat"

    headers = {}
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"

    payload = {
        "model": OLLAMA_CHAT_MODEL,
        "messages": messages,
        "stream": False,
    }

    try:
        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=120.0,
        )
        response.raise_for_status()

        result = response.json()
        answer = result.get("message", {}).get("content", "").strip()

        if not answer:
            raise RuntimeError("Ollama returned an empty response.")

        return answer

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Cannot connect to the configured Ollama service."
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Ollama request failed with status {exc.response.status_code}."
        ) from exc