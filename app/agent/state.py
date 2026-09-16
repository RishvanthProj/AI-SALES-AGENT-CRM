from typing import TypedDict, Optional, List, Dict, Any


class SalesAgentState(TypedDict, total=False):
    tenant_id: str
    lead_id: str
    contact_number: str
    lead_name: Optional[str]
    current_stage: str
    incoming_message: str
    need_summary: Optional[str]
    budget_signal: Optional[str]
    timeline_signal: Optional[str]
    qualification_score: float
    route_destination: Optional[str]
    reply_text: str
    history: List[Dict[str, str]]
    verified_products: List[Dict[str, Any]]
    inventory_data: Optional[Dict[str, Any]]
    business_info: Optional[Dict[str, Any]]
    extracted_sales: Optional[Dict[str, Any]]
    is_inappropriate: bool
    is_jailbreak: bool
    error: Optional[str]
