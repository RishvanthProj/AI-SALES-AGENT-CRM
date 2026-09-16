from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from app.schemas.ai import SalesExtraction, GroundedResponseContext
from app.schemas.agent import NeedExtraction, BudgetExtraction, TimelineExtraction


class AIProvider(ABC):
    """
    Abstract interface for AI conversational and extraction providers (Gemini, Claude, etc.).
    """

    @abstractmethod
    def extract_sales_signals(
        self,
        message_text: str,
        conversation_history: List[Dict[str, str]]
    ) -> SalesExtraction:
        """
        Extracts comprehensive structured sales entities, intent, signals, and security flags
        from the customer message.
        """
        pass

    @abstractmethod
    def extract_need(
        self,
        message_text: str,
        conversation_history: List[Dict[str, str]]
    ) -> NeedExtraction:
        """
        Extracts customer need and requirement summary.
        """
        pass

    @abstractmethod
    def extract_budget(self, message_text: str) -> BudgetExtraction:
        """
        Extracts structured budget signal.
        """
        pass

    @abstractmethod
    def extract_timeline(self, message_text: str) -> TimelineExtraction:
        """
        Extracts structured timeline signal.
        """
        pass

    @abstractmethod
    def generate_conversational_response(
        self,
        context: GroundedResponseContext
    ) -> str:
        """
        Generates a natural, human-like sales response grounded in verified Firebase facts.
        """
        pass

    @abstractmethod
    def generate_stage_copy(
        self,
        current_stage: str,
        lead_name: Optional[str],
        conversation_history: List[Dict[str, str]],
        extracted_signals: Dict[str, Any]
    ) -> str:
        """
        Generates copy for a specific stage.
        """
        pass
