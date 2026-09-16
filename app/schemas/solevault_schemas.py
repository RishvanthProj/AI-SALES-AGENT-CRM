from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Brands & Categories
# =============================================================================
class BrandDTO(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None
    website_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryDTO(BaseModel):
    id: int
    parent_category_id: Optional[int] = None
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    banner_url: Optional[str] = None
    display_order: int = 0
    product_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Product Images, Features, Variants & Reviews
# =============================================================================
class ProductImageDTO(BaseModel):
    id: int
    image_url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    image_type: str = "front"
    display_order: int = 1
    is_primary: bool = False

    model_config = ConfigDict(from_attributes=True)


class ProductVariantDTO(BaseModel):
    id: int
    product_id: int
    sku: str
    barcode: Optional[str] = None
    color: str
    color_code: Optional[str] = None
    size: str
    size_system: str = "UK"
    width: str = "Regular"
    gender: Optional[str] = None
    stock_quantity: int = 0
    available_quantity: int = 0
    price: float
    sale_price: float
    mrp: float
    weight: Optional[float] = 550.0
    image_url: Optional[str] = None
    status: str = "active"

    model_config = ConfigDict(from_attributes=True)


class ProductFeatureDTO(BaseModel):
    id: int
    feature_name: str
    feature_value: str
    display_order: int = 1

    model_config = ConfigDict(from_attributes=True)


class ReviewDTO(BaseModel):
    id: int
    user_name: Optional[str] = "Verified Customer"
    rating: int
    title: Optional[str] = None
    review_text: str
    verified_purchase: bool = True
    helpful_count: int = 0
    admin_response: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductListItemDTO(BaseModel):
    id: int
    name: str
    slug: str
    sku: str
    brand_name: Optional[str] = None
    category_name: Optional[str] = None
    short_description: Optional[str] = None
    technology: Optional[str] = None
    gender: str = "Unisex"
    sport: Optional[str] = None
    occasion: Optional[str] = None
    material: Optional[str] = None
    water_resistant: bool = False
    waterproof: bool = False
    breathable: bool = True
    cushioning_level: Optional[str] = None
    traction_level: Optional[str] = None
    sale_price: float
    mrp: float
    discount_percentage: float = 0.0
    rating_average: float = 4.5
    rating_count: int = 0
    available_quantity: int = 0
    featured: bool = False
    best_seller: bool = False
    new_arrival: bool = False
    limited_edition: bool = False
    primary_image: Optional[str] = None
    available_colors: List[str] = []
    available_sizes: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class ProductDetailDTO(ProductListItemDTO):
    long_description: Optional[str] = None
    upper_material: Optional[str] = None
    lining_material: Optional[str] = None
    insole_material: Optional[str] = None
    outsole_material: Optional[str] = None
    sole_type: Optional[str] = None
    closure_type: Optional[str] = None
    heel_type: Optional[str] = None
    toe_shape: Optional[str] = None
    shoe_width: Optional[str] = None
    shoe_height: Optional[str] = None
    weight: Optional[float] = None
    arch_support: Optional[str] = None
    country_of_origin: str = "India"
    manufacturer: Optional[str] = None
    warranty_period: str = "6 months"
    care_instructions: Optional[str] = None
    sustainability_information: Optional[str] = None
    images: List[ProductImageDTO] = []
    variants: List[ProductVariantDTO] = []
    features_list: List[ProductFeatureDTO] = []
    reviews: List[ReviewDTO] = []


# =============================================================================
# Cart & Checkout DTOs
# =============================================================================
class CartItemDTO(BaseModel):
    id: int
    product_id: int
    variant_id: int
    product_name: str
    sku: str
    size: str
    color: str
    image_url: Optional[str] = None
    quantity: int = 1
    unit_price: float
    discount: float = 0.0
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class CartDTO(BaseModel):
    id: Optional[int] = None
    items: List[CartItemDTO] = []
    item_count: int = 0
    subtotal: float = 0.0
    discount: float = 0.0
    coupon_code: Optional[str] = None
    coupon_discount: float = 0.0
    tax: float = 0.0
    shipping_fee: float = 0.0
    free_shipping_threshold: float = 1500.0
    amount_needed_for_free_shipping: float = 0.0
    total: float = 0.0
    currency: str = "INR"


class AddToCartRequest(BaseModel):
    product_id: int
    variant_id: int
    quantity: int = Field(default=1, ge=1, le=10)


class ApplyCouponRequest(BaseModel):
    code: str
    subtotal: float


class CheckoutRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    address_line_1: str
    address_line_2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = "India"
    shipping_method_id: int = 1
    payment_method: str = "UPI"  # UPI, Credit Card, Debit Card, Net Banking, Wallet, Cash on Delivery
    coupon_code: Optional[str] = None
    items: List[Dict[str, Any]]
    customer_notes: Optional[str] = None


class OrderResponseDTO(BaseModel):
    order_number: str
    total: float
    payment_status: str
    order_status: str
    shipping_status: str
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    estimated_delivery_date: Optional[str] = None
    placed_at: str
    item_count: int
    items: List[Dict[str, Any]]


# =============================================================================
# Reviews & Interactions
# =============================================================================
class ReviewCreateDTO(BaseModel):
    product_id: int
    rating: int = Field(ge=1, le=5)
    title: Optional[str] = None
    review_text: str = Field(min_length=5)
    user_name: Optional[str] = "Customer"
    user_email: Optional[str] = None


class ReviewVoteDTO(BaseModel):
    review_id: int
    is_helpful: bool = True


# =============================================================================
# Comparison & Recommendations
# =============================================================================
class CompareRequestDTO(BaseModel):
    product_ids: List[int] = Field(min_length=2, max_length=4)


# =============================================================================
# Admin KPIs & Analytics
# =============================================================================
class AdminKpisDTO(BaseModel):
    total_revenue: float
    today_revenue: float
    total_orders: int
    pending_orders: int
    total_customers: int
    total_products: int
    low_stock_products: int
    total_returns: int
    average_order_value: float


class AnalyticsChartDTO(BaseModel):
    revenue_by_day: List[Dict[str, Any]]
    orders_by_category: List[Dict[str, Any]]
    sales_by_gender: List[Dict[str, Any]]
    inventory_by_status: List[Dict[str, Any]]
