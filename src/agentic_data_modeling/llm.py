"""LLM factory — returns the configured chat model (OpenAI or Ollama)."""

from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel


def get_llm() -> BaseChatModel:
    """Return the chat model selected by ADM_PROVIDER (openai | ollama).

    OpenAI (default)
    ----------------
    Reads OPENAI_API_KEY and ADM_MODEL from the environment / .env file.

    Ollama (local)
    --------------
    Requires Ollama running at ADM_OLLAMA_BASE_URL (default: http://localhost:11434).
    Model is set by ADM_OLLAMA_MODEL (default: llama3.2).
    No API key needed.
    """
    from agentic_data_modeling.config import get_settings

    s = get_settings()

    if s.provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=s.ollama_model,
            base_url=s.ollama_base_url,
            temperature=s.temperature,
        )

    # Default: OpenAI
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=s.model,
        api_key=s.openai_api_key,
        temperature=s.temperature,
        max_tokens=s.max_tokens,
    )
