
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_EMBED_MODEL = os.getenv(
    "OLLAMA_EMBED_MODEL",
    "nomic-embed-text:latest",
)

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "").strip()


def create_embedding(text: str) -> list[float]:
    """Generate a vector embedding using Ollama."""

    headers = {}
    if OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {OLLAMA_API_KEY}"

    try:
        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={
                "model": OLLAMA_EMBED_MODEL,
                "input": text,
            },
            headers=headers,
            timeout=60.0,
        )
        response.raise_for_status()

        result = response.json()
        embeddings = result.get("embeddings", [])

        if not embeddings or not embeddings[0]:
            raise RuntimeError("Ollama returned an empty embedding.")

        embedding = embeddings[0]

        if len(embedding) != 768:
            raise RuntimeError(
                f"Expected 768 dimensions, received {len(embedding)}."
            )

        return embedding

    except httpx.RequestError as exc:
        raise RuntimeError(
            "Cannot connect to the Ollama embedding service."
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Ollama embedding request failed with status "
            f"{exc.response.status_code}."
        ) from exc
