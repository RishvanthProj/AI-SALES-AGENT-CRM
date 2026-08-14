import json
import re
from typing import Optional, Dict, Any, List
import anthropic
from app.config import settings
from app.schemas.agent import NeedExtraction, BudgetExtraction, TimelineExtraction, NodeLanguageOutput


class ClaudeService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = settings.CLAUDE_MODEL
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key and self.api_key.startswith("sk-") else None

    def extract_need(self, message_text: str, conversation_history: List[Dict[str, str]]) -> NeedExtraction:
        """
        Extracts customer need and problem definition from conversation text.
        """
        if not self.client:
            return NeedExtraction(
                summary=message_text.strip() or "General inquiry",
                category="General",
                clarity_score=0.85
            )

        prompt = f"""You are a precise data extraction tool. Extract the core customer requirement from the following WhatsApp conversation.
Do NOT decide the next stage. Only extract the structured fields.

Customer message: "{message_text}"

Return JSON matching this schema:
{{
  "summary": "concise description of what the user needs",
  "category": "product or service category",
  "clarity_score": 0.0 to 1.0
}}
"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_json = self._extract_json_block(response.content[0].text)
            return NeedExtraction.model_validate_json(raw_json)
        except Exception:
            return NeedExtraction(
                summary=message_text.strip() or "General inquiry",
                category="General",
                clarity_score=0.75
            )

    def extract_budget(self, message_text: str) -> BudgetExtraction:
        """
        Extracts structured budget signal (amount/range) from message text.
        """
        # Fast regex fallback for common budget patterns
        budget_pattern = re.search(r'(\$?\s?\d+[\d,.]*\s?(?:k|kilo|usd|eur|dollars|inr)?(?:\s?-\s?\$?\s?\d+[\d,.]*\s?(?:k|kilo|usd|eur|dollars|inr)?)?)', message_text, re.IGNORECASE)

        if not self.client:
            raw_match = budget_pattern.group(0).strip() if budget_pattern else message_text.strip()
            is_valid = bool(re.search(r'\d', raw_match))
            return BudgetExtraction(
                raw_text=message_text,
                budget_range=raw_match if is_valid else (message_text.strip() if len(message_text) < 50 else None),
                is_provided=is_valid or len(message_text.strip()) > 0,
                confidence=0.85
            )

        prompt = f"""You are a precise data extraction engine. Extract budget information from this user response.
Do NOT decide any workflow stage.

User text: "{message_text}"

Return JSON matching:
{{
  "raw_text": "{message_text}",
  "budget_range": "normalized budget string, e.g. '$10,000' or '$5k-$10k', or null if no budget mentioned",
  "is_provided": true/false,
  "confidence": 0.0 to 1.0
}}
"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_json = self._extract_json_block(response.content[0].text)
            return BudgetExtraction.model_validate_json(raw_json)
        except Exception:
            raw_match = budget_pattern.group(0).strip() if budget_pattern else message_text.strip()
            return BudgetExtraction(
                raw_text=message_text,
                budget_range=raw_match,
                is_provided=bool(raw_match),
                confidence=0.75
            )

    def extract_timeline(self, message_text: str) -> TimelineExtraction:
        """
        Extracts timeline requirement signal from message text.
        """
        if not self.client:
            urgent_keywords = ["urgent", "asap", "immediately", "today", "tomorrow", "this week"]
            is_urgent = any(w in message_text.lower() for w in urgent_keywords)
            return TimelineExtraction(
                raw_text=message_text,
                timeline_str=message_text.strip() if message_text else "Standard",
                is_provided=bool(message_text.strip()),
                is_urgent=is_urgent,
                confidence=0.85
            )

        prompt = f"""You are a precise data extraction engine. Extract the project timeline or deadline from this response.
Do NOT decide any workflow stage.

User text: "{message_text}"

Return JSON matching:
{{
  "raw_text": "{message_text}",
  "timeline_str": "normalized timeline string, e.g. 'Within 2 weeks', 'Next month', 'Q3', or null",
  "is_provided": true/false,
  "is_urgent": true/false,
  "confidence": 0.0 to 1.0
}}
"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_json = self._extract_json_block(response.content[0].text)
            return TimelineExtraction.model_validate_json(raw_json)
        except Exception:
            return TimelineExtraction(
                raw_text=message_text,
                timeline_str=message_text.strip(),
                is_provided=bool(message_text.strip()),
                is_urgent=False,
                confidence=0.75
            )

    def generate_stage_copy(
        self,
        current_stage: str,
        lead_name: Optional[str],
        conversation_history: List[Dict[str, str]],
        extracted_signals: Dict[str, Any]
    ) -> str:
        """
        Generates natural conversational copy for the current node stage.
        The LLM only generates the text matching the node's specific purpose.
        """
        stage_instructions = {
            "greet": "Welcome the customer warmly, introduce our service, and ask how we can help them today.",
            "qualify": "Acknowledge their interest and ask 1 clarifying question to understand their primary requirement or goal.",
            "collect_budget": "Acknowledge their use-case and politely ask for their estimated budget range or investment target so we can tailor the right solution.",
            "collect_timeline": "Acknowledge their budget and ask what their target timeline or ideal start date is.",
            "score": "Acknowledge all requirements received and inform them we are evaluating the best proposal.",
            "route": "Deliver final routing communication: if qualified, present quote initiation; if nurture, offer informative resources; if human handoff, state an account executive will connect shortly."
        }

        instruction = stage_instructions.get(current_stage, "Provide a helpful, polite WhatsApp sales response.")

        if not self.client:
            # Deterministic clean fallback templates
            templates = {
                "greet": f"Hello {lead_name or 'there'}! 👋 Welcome to our sales team. How can we help you achieve your goals today?",
                "qualify": "Thanks for reaching out! Could you share a bit more about the specific features or solution you are looking for?",
                "collect_budget": "Got it! To ensure we tailor the exact right package for you, what is your estimated budget or investment range for this project?",
                "collect_timeline": "Understood. When would you ideally like to kick off or have this solution in place?",
                "score": "Thank you for sharing those details! We're reviewing your requirements now.",
                "route": f"Fantastic! Based on your budget ({extracted_signals.get('budget_signal', 'stated')}) and timeline ({extracted_signals.get('timeline_signal', 'stated')}), we've prepared your custom quote. An expert will share full specs with you!"
            }
            return templates.get(current_stage, "Thank you for your message. An executive will reach out to you shortly.")

        prompt = f"""You are a professional WhatsApp sales qualification assistant.
CURRENT FIXED STAGE: {current_stage}
OBJECTIVE FOR THIS STAGE: {instruction}
CUSTOMER NAME: {lead_name or 'Friend'}
KNOWN SIGNALS: {json.dumps(extracted_signals)}

Write a concise (1-3 sentences), warm, professional WhatsApp message matching this stage objective.
Do NOT decide stage progression. Only write the message content.
"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=350,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception:
            return f"Thank you for contacting us. We've recorded your {current_stage} details."

    def _extract_json_block(self, text: str) -> str:
        text = text.strip()
        if "```json" in text:
            match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
            if match:
                return match.group(1)
        if "```" in text:
            match = re.search(r'```\s*([\s\S]*?)\s*```', text)
            if match:
                return match.group(1)
        return text


claude_service = ClaudeService()
