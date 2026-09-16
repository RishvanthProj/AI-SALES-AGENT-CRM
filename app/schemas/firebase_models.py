from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator, ConfigDict


class ProductVariant(BaseModel):
    variant_id: str
    size: Optional[str] = None
    color: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    stock: int = 0


class ProductDocument(BaseModel):
    """
    Comprehensive Shoe Product schema containing all technical, sizing,
    pricing, inventory, materials, and AI search attributes for StrideHub Shoes.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default="", alias="productId")
    businessId: str = "stridehub-shoes"
    sku: str = ""
    barcode: Optional[str] = None
    name: str
    brand: str = "StrideHub"
    category: str = "Running" # Running, Casual, Formal, Trail, Sneaker, Walking, Training
    subcategory: Optional[str] = None
    variety: Optional[str] = None
    gender: Optional[str] = "Unisex" # Men, Women, Unisex
    ageGroup: Optional[str] = "Adult"
    collection: Optional[str] = "2026 Performance"
    description: str = ""
    aiDescription: Optional[str] = None
    primaryColor: Optional[str] = "Black"
    secondaryColor: Optional[str] = None
    colorFamily: Optional[str] = "Dark"
    pattern: Optional[str] = "Solid"
    upperMaterial: Optional[str] = "Breathable Engineered Mesh"
    liningMaterial: Optional[str] = "Soft Padded Fabric"
    insoleMaterial: Optional[str] = "Ergonomic Memory Foam"
    midsoleMaterial: Optional[str] = "Responsive EVA Cushion"
    outsoleMaterial: Optional[str] = "High-Traction Anti-Slip Rubber"
    closureType: Optional[str] = "Lace-Up"
    heelType: Optional[str] = "Flat"
    heelHeight: Optional[str] = "Zero Drop"
    toeShape: Optional[str] = "Round Toe"
    waterResistance: Optional[str] = "Water Resistant Coating"
    breathability: Optional[str] = "High Breathability"
    slipResistance: Optional[str] = "Certified Anti-Slip"
    comfortLevel: Optional[str] = "Maximum Comfort"
    cushioning: Optional[str] = "Ultra Plush"
    supportLevel: Optional[str] = "Neutral to High Arch"
    archSupport: Optional[str] = "Medium Arch"
    flexibility: Optional[str] = "High Flexibility"
    stability: Optional[str] = "Motion Control"
    weight: Optional[str] = "280g (Size 9)"
    dimensions: Optional[str] = "32 x 20 x 12 cm"
    sizeSystem: str = "UK/India"
    availableSizes: List[str] = Field(default_factory=lambda: ["5", "6", "7", "8", "9", "10", "11", "12"])
    fitType: Optional[str] = "Regular Fit"
    trueToSize: Optional[bool] = True
    careInstructions: Optional[str] = "Wipe with damp cloth. Air dry away from direct sunlight."
    expectedLifetime: Optional[str] = "800 - 1,000 km / 18 Months"
    durabilityRating: Optional[float] = 4.8
    recommendedSurface: Optional[str] = "Road, Track, Treadmill"
    price: float = 1499.0
    mrp: float = 1999.0
    salePrice: Optional[float] = None
    discountPercent: Optional[float] = 35.0
    currency: str = "INR"
    quantity: int = 0
    stockStatus: str = "in_stock" # in_stock, low_stock, out_of_stock
    lowStockThreshold: int = 5
    warehouse: Optional[str] = "Central Bengaluru Hub"
    restockDate: Optional[str] = None
    shippingAvailable: bool = True
    deliveryRegions: List[str] = Field(default_factory=lambda: ["All India", "Metro Cities (24-48h)", "Tier 2/3 (3-5 days)"])
    dispatchTime: Optional[str] = "Same day dispatch before 3 PM"
    deliveryTime: Optional[str] = "3 - 5 business days"
    codAvailable: bool = True
    pickupAvailable: bool = True
    returnAvailable: bool = True
    returnWindow: str = "7 Days Easy Returns"
    exchangeAvailable: bool = True
    exchangeWindow: str = "15 Days Size Exchange"
    warrantyMonths: int = 6
    warrantyType: Optional[str] = "Manufacturing Defect Warranty"
    rating: float = 4.7
    reviewCount: int = 142
    supplier: Optional[str] = "StrideHub Manufacturing Ltd"
    countryOfOrigin: Optional[str] = "India"
    aiSearchable: bool = True
    aiRecommendable: bool = True
    relatedProducts: List[str] = Field(default_factory=list)
    crossSellProducts: List[str] = Field(default_factory=list)
    upsellProduct: Optional[str] = None
    imageUrl: Optional[str] = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80"
    variants: List[ProductVariant] = Field(default_factory=list)
    sizes: List[str] = Field(default_factory=list)
    colors: List[str] = Field(default_factory=list)
    specifications: Dict[str, Any] = Field(default_factory=dict)
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # ID normalization
            if "id" in data and "productId" not in data:
                data["productId"] = data["id"]
            elif "productId" in data and "id" not in data:
                data["id"] = data["productId"]
            elif not data.get("id") and not data.get("productId"):
                data["id"] = "prod-" + str(hash(data.get("name", "")))[:8]
                data["productId"] = data["id"]

            # Sale price normalization
            if "sale_price" in data and "salePrice" not in data:
                data["salePrice"] = data["sale_price"]
            elif "salePrice" in data and "sale_price" not in data:
                data["sale_price"] = data["salePrice"]

            # Quantity normalization
            if "available_quantity" in data and "quantity" not in data:
                data["quantity"] = data["available_quantity"]
            elif "quantity" in data and "available_quantity" not in data:
                data["available_quantity"] = data["quantity"]

            # Sizes normalization
            if "sizes" in data and not data.get("availableSizes"):
                data["availableSizes"] = data["sizes"]
            elif "availableSizes" in data and not data.get("sizes"):
                data["sizes"] = data["availableSizes"]
        return data

    @property
    def productId(self) -> str:
        return self.id

    @property
    def effective_price(self) -> float:
        if self.salePrice is not None and self.salePrice > 0:
            return self.salePrice
        return self.price

    @property
    def available_quantity(self) -> int:
        return self.quantity


class FAQDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    businessId: str = "stridehub-shoes"
    question: str
    answer: str
    category: str = "general"


class OfferDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    businessId: str = "stridehub-shoes"
    code: str
    title: str
    description: str
    discount_pct: Optional[float] = None
    flat_discount: Optional[float] = None
    min_order_amount: float = 0.0
    is_active: bool = True
    valid_until: Optional[str] = None


class CustomerDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    businessId: str = "stridehub-shoes"
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    shoe_size_preference: Optional[str] = None
    preferred_category: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    previous_interactions: List[Dict[str, Any]] = Field(default_factory=list)
    previous_orders: List[str] = Field(default_factory=list)
    customer_stage: str = "lead"
    lead_status: str = "active"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class OrderItemDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    product_id: str
    product_name: str
    size: str
    color: str
    quantity: int
    unit_price: float
    total_price: float


class OrderDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    order_id: str
    businessId: str = "stridehub-shoes"
    customer_id: str
    customer_name: str
    contact_number: str
    items: List[OrderItemDocument] = Field(default_factory=list)
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    quantity: int = 1
    amount: float = 0.0
    payment_method: str = "Cash on Delivery"
    payment_status: str = "pending"
    status: str = "confirmed"
    delivery_address: str = "Bangalore, Karnataka"
    courier_partner: str = "BlueDart Express"
    tracking_id: str = "BD982341IN"
    estimated_delivery: str = "3-4 Business Days"
    order_date: Optional[str] = None
    delivery_info: Dict[str, Any] = Field(default_factory=dict)


class BusinessSettingsDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    businessId: str = "stridehub-shoes"
    business_name: str = "StrideHub Shoes"
    business_description: str = "Premium Performance, Casual, & Formal Footwear Engineered for Comfort"
    address: str = "StrideHub Flagship Store, 100ft Road, Indiranagar, Bengaluru, KA 560038"
    working_hours: str = "9:00 AM - 9:00 PM (Monday - Sunday)"
    contact_details: Dict[str, str] = Field(default_factory=lambda: {
        "phone": "+91 80 4123 9876",
        "whatsapp": "+91 98765 43210",
        "email": "support@stridehub.in",
        "website": "https://stridehub.in"
    })
    shipping_information: str = "Free shipping on orders above ₹999. Delivered in 3-5 business days across India."
    payment_methods: List[str] = Field(default_factory=lambda: ["UPI (GPay/PhonePe)", "Credit/Debit Card", "Cash on Delivery", "Net Banking"])
    return_refund_policy: str = "7-day hassle-free return window for unworn shoes with original packaging."
    exchange_policy: str = "15-day free size exchange available if the fit isn't perfect."
    cancellation_policy: str = "Orders can be cancelled anytime before dispatch with instant full refund."
    available_offers: List[Dict[str, Any]] = Field(default_factory=list)
    loyalty_rules: Dict[str, Any] = Field(default_factory=dict)
    follow_up_rules: Dict[str, Any] = Field(default_factory=dict)


class LeadCRMDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    lead_id: str
    businessId: str = "stridehub-shoes"
    contact_number: str
    name: Optional[str] = None
    stage: str = "greet"
    qualification_score: float = 0.0
    budget_signal: Optional[str] = None
    timeline_signal: Optional[str] = None
    need_summary: Optional[str] = None
    route_destination: Optional[str] = None
    last_interaction: Optional[str] = None
    follow_up_state: Optional[str] = "pending"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    updated_at: Optional[str] = None


class AutomationRuleDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    rule_id: str
    businessId: str = "stridehub-shoes"
    name: str
    trigger: str
    delay_hours: int = 24
    is_active: bool = True
    template_message: str


class SupportTicketDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    ticket_id: str
    businessId: str = "stridehub-shoes"
    customer_id: str
    customer_name: str
    issue: str
    status: str = "open"
    priority: str = "high"
    assigned_to: Optional[str] = "Human Sales Lead"
    created_at: Optional[str] = None


class ConversationMessageDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    message_id: str
    businessId: str = "stridehub-shoes"
    conversation_id: str
    role: str
    content: str
    timestamp: str
    whatsapp_message_id: Optional[str] = None
    raw_payload: Dict[str, Any] = Field(default_factory=dict)
