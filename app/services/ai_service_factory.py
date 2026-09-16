from app.config import settings
from app.services.ai_provider import AIProvider
from app.services.gemini_service import gemini_service
from app.services.claude_service import claude_service


def get_ai_provider() -> AIProvider:
    """
    Factory that returns the configured AI provider.
    Defaults to GeminiService ('gemini').
    """
    provider_name = (settings.AI_PROVIDER or "gemini").lower()
    if provider_name == "claude":
        return claude_service
    return gemini_service


# Default AI provider instance
ai_service = get_ai_provider()
