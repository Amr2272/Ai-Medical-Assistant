from langchain_groq import ChatGroq

from src.config import (
    GROQ_API_KEY,
    LLM_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
)


class LLMManager:
    """
    Manages the LLM lifecycle.
    Singleton pattern to ensure only one client instance is created.
    """

    _instance = None
    _llm = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_llm(self) -> ChatGroq:
        """
        Get or create the LLM instance.

        Returns:
            ChatGroq: The configured chat model.
        """
        if self._llm is None:
            self._llm = self._load_llm()
        return self._llm

    def _load_llm(self) -> ChatGroq:
        """Create the Groq-backed chat model."""

        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set. Create a free key at "
                "https://console.groq.com/keys, then add it to a `.env` "
                "file in the project root:\n\n    GROQ_API_KEY=your_key_here\n"
            )

        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )

        return llm

    def clear(self):
        """Drop the cached client (e.g. to pick up a new model/config)."""
        self._llm = None


# Singleton accessor function
def get_llm() -> ChatGroq:
    """Get the LLM instance"""
    return LLMManager().get_llm()
