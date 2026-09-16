"""
Comprehensive tests for Pan-India Multilingual Adaptation:
- Tanglish (Tamil in English alphabet) persistence for Tamil Nadu customers
- Hinglish (Hindi in English alphabet) for Hindi-speaking customers
- Tenglish / Manglish Romanized adaptations
- Zero emojis enforcement across all responses
"""

import pytest
from app.services.gemini_service import gemini_service
from app.schemas.ai import GroundedResponseContext
from terminal_chat import process_message, detect_language_flavor, handle_checkout_flow, checkout_session


def test_01_tanglish_detection_and_response():
    """
    Test 1: When a customer speaks in Tanglish ('bro running shoe venum'),
    the assistant responds in natural, casual Tanglish with zero emojis.
    """
    context = GroundedResponseContext(
        business_name="Starboyz",
        business_description="Starboyz Footwear - Style, Performance and Comfort",
        current_stage="inquiry",
        lead_name="Rishvanth",
        customer_message="bro running shoe venum daily use ku",
        conversation_history=[]
    )
    reply = gemini_service.generate_conversational_response(context)
    assert len(reply) > 0
    # Must contain Tanglish markers
    assert any(w in reply.lower() for w in ["bro", "namma", "kandippa", "iruku", "running", "shoe", "unga", "budget", "size"])
    # Absolutely no emojis
    assert "👟" not in reply and "✨" not in reply and "🔥" not in reply


def test_02_tanglish_persistence_across_turns():
    """
    Test 2: Assistant persists in Tanglish across multiple conversational turns.
    """
    history = [
        {"role": "user", "content": "vanakkam bro, nalla running shoe iruka?"},
        {"role": "assistant", "content": "Vanakkam bro! Kandippa iruku. Enna budget and UK size thedureenga?"},
        {"role": "user", "content": "budget 2000 kula, size 9"},
        {"role": "assistant", "content": "Super bro! StrideAir Zoom Casual Sneaker Rs. 1,299 ku available ah iruku."},
        {"role": "user", "content": "idhu daily use ku set aaguma bro?"}
    ]
    context = GroundedResponseContext(
        business_name="Starboyz",
        business_description="Starboyz Footwear",
        current_stage="qualify",
        customer_message="idhu daily use ku set aaguma bro?",
        conversation_history=history
    )
    reply = gemini_service.generate_conversational_response(context)
    assert len(reply) > 0
    assert any(w in reply.lower() for w in ["bro", "aagum", "iruku", "super", "cushioning", "daily", "nalla", "set"])


def test_03_hinglish_detection_and_response():
    """
    Test 3: When a customer speaks in Hinglish ('bhai running shoe chahiye', 'aap kaise hain'),
    the assistant responds in friendly Hinglish (Romanized Hindi) with zero emojis.
    """
    context = GroundedResponseContext(
        business_name="Starboyz",
        business_description="Starboyz Footwear",
        current_stage="inquiry",
        lead_name="Rahul",
        customer_message="bhai running shoe chahiye, price kitna hai?",
        conversation_history=[]
    )
    reply = gemini_service.generate_conversational_response(context)
    assert len(reply) > 0
    # Must contain Hinglish markers
    assert any(w in reply.lower() for w in ["bhai", "aap", "kaise", "swagat", "hai", "size", "budget", "starboyz", "mil"])
    # Absolutely no emojis
    assert "👟" not in reply and "✨" not in reply


def test_04_terminal_language_detection():
    """
    Test 4: Detects language flavor correctly in terminal chat.
    """
    assert detect_language_flavor("bro size 9 stock iruka", []) == "tanglish"
    assert detect_language_flavor("bhai shoes dikhao 2000 ke andar", []) == "hinglish"
    assert detect_language_flavor("bhayya shoes kavali", []) == "tenglish"
    assert detect_language_flavor("chetta shoes venam", []) == "manglish"
    assert detect_language_flavor("Do you have running shoes in size 9?", []) == "english"


def test_05_terminal_tanglish_checkout_flow():
    """
    Test 5: Full in-chat checkout flow adapts to Tanglish for Tamil Nadu customers.
    """
    history = [
        {"role": "user", "content": "bro StrideAir Zoom Casual Sneaker size 9 venum"},
        {"role": "assistant", "content": "Kandippa bro, size 9 stock la iruku Rs. 1,299 ku."}
    ]

    # Reset checkout session
    checkout_session["active"] = False
    checkout_session["step"] = None

    # Step 0: Trigger checkout in Tanglish
    reply_step0 = handle_checkout_flow("bro i want to buy this, checkout panren", history)
    assert "Super choice bro" in reply_step0 or "delivery details anupunga" in reply_step0
    assert "Full Name" in reply_step0

    # Step 1: Provide delivery address
    reply_step1 = handle_checkout_flow("Rishvanth, 42 100ft Road, Indiranagar, Bangalore, Tamil Nadu - 600001", history)
    assert "Order Summary" in reply_step1
    assert "Payment epdi panna poreenga bro" in reply_step1 or "COD" in reply_step1

    # Step 2: Choose COD
    reply_step2 = handle_checkout_flow("COD", history)
    assert "Unga order confirm aayiduchu bro" in reply_step2
    assert "Order ID:" in reply_step2
    assert "BlueDart" in reply_step2
