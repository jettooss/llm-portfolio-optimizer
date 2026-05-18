from __future__ import annotations

import os
from pathlib import Path


DEFAULT_OPENAI_MODEL = "openai/gpt-oss-20b"
DEFAULT_OPENAI_LARGE_MODEL = "openai/gpt-oss-120b"
DEFAULT_OPENAI_BASE_URL = "https://routerai.ru/api/v1"
DEFAULT_GIGACHAT_MODEL = "GigaChat-2-Max"
DEFAULT_DEEPSEEK_MODEL = "deepseek/deepseek-v4-pro"
DEFAULT_GEMINI_MODEL = "google/gemini-3.1-pro-preview"
DEFAULT_QWEN_MODEL = "qwen/qwen3.5-35b-a3b"
DEFAULT_MISTRAL_MODEL = "mistralai/mistral-small-2603"

DEFAULT_RETURN_RISK_MODELS = (
    DEFAULT_OPENAI_MODEL,
    DEFAULT_OPENAI_LARGE_MODEL,
    DEFAULT_DEEPSEEK_MODEL,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_QWEN_MODEL,
    DEFAULT_MISTRAL_MODEL,
)

DEFAULT_GIGACHAT_RETURN_RISK_MODELS = (
    f"gigachat:{DEFAULT_GIGACHAT_MODEL}",
    "gigachat:GigaChat-2-Lite",
)


def load_env_file(path: str | Path = ".env") -> None:
    """Load simple KEY=VALUE lines without requiring python-dotenv."""
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def configure_llm_environment(env_path: str | Path = ".env") -> None:
    load_env_file(env_path)
    os.environ.setdefault("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    os.environ.setdefault("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL)
    os.environ.setdefault("OPENAI_TIMEOUT", "180")
    os.environ.setdefault("GIGACHAT_MODEL", DEFAULT_GIGACHAT_MODEL)
    os.environ.setdefault("GIGACHAT_TIMEOUT", "180")
    os.environ.setdefault("DEEPSEEK_MODEL", DEFAULT_DEEPSEEK_MODEL)
    os.environ.setdefault("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
    os.environ.setdefault("QWEN_MODEL", DEFAULT_QWEN_MODEL)
    os.environ.setdefault("MISTRAL_MODEL", DEFAULT_MISTRAL_MODEL)


def _split_models(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def get_return_risk_models() -> list[str]:
    configured_models = _split_models(os.environ.get("RETURN_RISK_MODELS"))
    models = configured_models or list(DEFAULT_RETURN_RISK_MODELS)
    if not configured_models and (os.environ.get("GIGACHAT_CREDENTIALS") or os.environ.get("GIGACHAT_ACCESS_TOKEN")):
        models.extend(DEFAULT_GIGACHAT_RETURN_RISK_MODELS)

    seen = set()
    unique_models = []
    for model in models:
        if model not in seen:
            seen.add(model)
            unique_models.append(model)
    return unique_models
