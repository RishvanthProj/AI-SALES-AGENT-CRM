import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Boolean,
    Float,
    Numeric,
    DateTime,
    Date,
    ForeignKey,
    Text,
    UniqueConstraint,
    Index,
    JSON
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()
JSONType = JSON().with_variant(JSONB, "postgresql")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# =============================================================================
# 1. USERS & ADDRESSES
# =============================================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)  # male, female, other, unisex
    profile_image = Column(String(500), nullable=True)
    role = Column(String(50), default="customer", nullable=False)  # customer, admin, manager, inventory_manager, support_agent
    status = Column(String(50), default="active", nullable=False)  # active, suspended, blocked
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(50), nullable=True)
    preferred_language = Column(String(20), default="en")
    preferred_currency = Column(String(10), default="INR")
    newsletter_subscribed = Column(Boolean, default=False)
    marketing_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    addresses = relationship("CustomerAddress", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    wishlists = relationship("Wishlist", back_populates="user")
    carts = relationship("Cart", back_populates="user")


class CustomerAddress(Base):
    __tablename__ = "customer_addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    address_type = Column(String(50), default="home")  # home, office, other
    recipient_name = Column(String(150), nullable=False)
    phone = Column(String(50), nullable=False)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    landmark = Column(String(150), nullable=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    country = Column(String(100), default="India", nullable=False)
    postal_code = Column(String(20), nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_default_shipping = Column(Boolean, default=False)
    is_default_billing = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="addresses")


# =============================================================================
# 2. BRANDS & CATEGORIES
# =============================================================================
class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    products = relationship("Product", back_populates="brand")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String(150), nullable=False)
    slug = Column(String(150), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(500), nullable=True)
    display_order = Column(Integer, default=0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    parent = relationship("Category", remote_side=[id], backref="subcategories")
    products = relationship("Product", back_populates="category", foreign_keys="Product.category_id")


# =============================================================================
# 3. PRODUCTS & ATTRIBUTES (100+ Fields)
# =============================================================================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    subcategory_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)

    # Core Identifiers
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    product_code = Column(String(100), nullable=True, index=True)
    short_description = Column(String(500), nullable=True)
    long_description = Column(Text, nullable=True)

    # Material & Construction
    material = Column(String(150), nullable=True)
    upper_material = Column(String(150), nullable=True)
    lining_material = Column(String(150), nullable=True)
    insole_material = Column(String(150), nullable=True)
    outsole_material = Column(String(150), nullable=True)
    sole_type = Column(String(100), nullable=True)
    closure_type = Column(String(100), nullable=True)  # Lace-Up, Slip-On, Velcro, Zipper
    heel_type = Column(String(100), nullable=True)
    toe_shape = Column(String(100), nullable=True)  # Round, Pointed, Square
    shoe_width = Column(String(50), nullable=True)  # Narrow, Regular, Wide, Extra Wide
    shoe_height = Column(String(50), nullable=True)  # Low-Top, Mid-Top, High-Top
    weight = Column(Float, nullable=True)  # grams
    heel_height = Column(Float, default=0.0)  # mm
    platform_height = Column(Float, default=0.0)  # mm

    # Technical Capabilities
    water_resistant = Column(Boolean, default=False)
    waterproof = Column(Boolean, default=False)
    breathable = Column(Boolean, default=True)
    shock_absorption = Column(String(100), nullable=True)
    arch_support = Column(String(100), nullable=True)
    cushioning_level = Column(String(100), nullable=True)  # Low, Medium, High, Maximum
    flexibility_level = Column(String(100), nullable=True)
    traction_level = Column(String(100), nullable=True)
    durability_rating = Column(Float, default=4.5)
    comfort_rating = Column(Float, default=4.5)

    # Classification & Demographics
    occasion = Column(String(100), nullable=True)  # Casual, Sports, Formal, Party, Outdoor
    sport = Column(String(100), nullable=True)  # Running, Training, Basketball, Football, Trekking
    gender = Column(String(50), default="Unisex", index=True)  # Men, Women, Kids, Unisex
    age_group = Column(String(50), default="Adult")  # Adult, Kids, Teen
    season = Column(String(50), nullable=True)  # All Season, Summer, Winter, Monsoon
    collection = Column(String(100), nullable=True)
    style = Column(String(100), nullable=True)
    fit_type = Column(String(50), default="Regular")  # Regular, Slim, Relaxed
    size_type = Column(String(20), default="UK")  # UK, US, EU, CM

    # Manufacturer & Compliance
    country_of_origin = Column(String(100), default="India")
    manufacturer = Column(String(200), nullable=True)
    manufacturer_part_number = Column(String(100), nullable=True)
    warranty_period = Column(String(100), default="6 months")
    care_instructions = Column(Text, nullable=True)
    features = Column(Text, nullable=True)
    technology = Column(String(255), nullable=True)  # e.g., Air Cushion, Memory Foam, Carbon Plate
    certifications = Column(String(255), nullable=True)
    sustainability_information = Column(Text, nullable=True)

    # Stock & Pricing
    available_quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)
    low_stock_threshold = Column(Integer, default=5, nullable=False)
    base_price = Column(Numeric(12, 2), nullable=False)
    sale_price = Column(Numeric(12, 2), nullable=False, index=True)
    cost_price = Column(Numeric(12, 2), nullable=True)
    mrp = Column(Numeric(12, 2), nullable=False)
    tax_rate = Column(Float, default=18.0)  # 18% GST standard
    discount_percentage = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")

    # Visibility & Merchandising Flags
    status = Column(String(50), default="active", index=True)  # active, draft, archived
    visibility = Column(Boolean, default=True)
    featured = Column(Boolean, default=False, index=True)
    best_seller = Column(Boolean, default=False, index=True)
    new_arrival = Column(Boolean, default=False, index=True)
    limited_edition = Column(Boolean, default=False, index=True)
    pre_order = Column(Boolean, default=False)
    release_date = Column(Date, nullable=True)
    publish_date = Column(Date, nullable=True)

    # Performance Analytics Counters
    rating_average = Column(Float, default=0.0, index=True)
    rating_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    purchase_count = Column(Integer, default=0)
    wishlist_count = Column(Integer, default=0)
    return_rate = Column(Float, default=0.0)

    # SEO & Metadata
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(500), nullable=True)
    meta_keywords = Column(String(500), nullable=True)
    canonical_url = Column(String(500), nullable=True)

    # Timestamps & Soft Deletes
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    brand = relationship("Brand", back_populates="products")
    category = relationship("Category", back_populates="products", foreign_keys=[category_id])
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.display_order")
    videos = relationship("ProductVideo", back_populates="product", cascade="all, delete-orphan")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    feature_items = relationship("ProductFeature", back_populates="product", cascade="all, delete-orphan")
    tag_mappings = relationship("ProductTagMapping", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product")
    questions = relationship("ProductQuestion", back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    alt_text = Column(String(255), nullable=True)
    image_type = Column(String(50), default="front")  # front, back, side, top, bottom, inside, lifestyle, 360, video_thumbnail
    display_order = Column(Integer, default=1)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    product = relationship("Product", back_populates="images")


class ProductVideo(Base):
    __tablename__ = "product_videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    video_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(Integer, default=30)  # seconds
    video_type = Column(String(50), default="demo")
    display_order = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    product = relationship("Product", back_populates="videos")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    barcode = Column(String(100), nullable=True, index=True)
    color = Column(String(100), nullable=False)
    color_code = Column(String(20), nullable=True)  # Hex code
    size = Column(String(20), nullable=False)  # 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
    size_system = Column(String(20), default="UK")  # UK, US, EU, CM
    width = Column(String(50), default="Regular")
    material_variant = Column(String(100), nullable=True)
    gender = Column(String(50), default="Unisex")
    stock_quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)
    available_quantity = Column(Integer, default=0, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    sale_price = Column(Numeric(12, 2), nullable=False)
    mrp = Column(Numeric(12, 2), nullable=False)
    weight = Column(Float, default=550.0)
    image_url = Column(String(500), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    product = relationship("Product", back_populates="variants")
    inventory_records = relationship("Inventory", back_populates="variant")


class ProductColor(Base):
    __tablename__ = "product_colors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    hex_code = Column(String(20), nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class ProductSize(Base):
    __tablename__ = "product_sizes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    size = Column(String(20), nullable=False)
    size_system = Column(String(20), default="UK")  # UK, US, EU, CM
    foot_length_cm = Column(Float, nullable=False)
    gender = Column(String(50), default="Unisex")
    age_group = Column(String(50), default="Adult")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class ProductFeature(Base):
    __tablename__ = "product_features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_name = Column(String(150), nullable=False)
    feature_value = Column(String(255), nullable=False)
    display_order = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    product = relationship("Product", back_populates="feature_items")


class ProductTag(Base):
    __tablename__ = "product_tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class ProductTagMapping(Base):
    __tablename__ = "product_tag_mapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_id = Column(Integer, ForeignKey("product_tags.id", ondelete="CASCADE"), nullable=False, index=True)

    product = relationship("Product", back_populates="tag_mappings")
    tag = relationship("ProductTag")


# =============================================================================
# 4. WAREHOUSES & INVENTORY
# =============================================================================
class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), default="India")
    postal_code = Column(String(20), nullable=False)
    manager_name = Column(String(150), nullable=True)
    manager_phone = Column(String(50), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)
    available_quantity = Column(Integer, default=0, nullable=False)
    damaged_quantity = Column(Integer, default=0, nullable=False)
    incoming_quantity = Column(Integer, default=0, nullable=False)
    reorder_level = Column(Integer, default=5, nullable=False)
    reorder_quantity = Column(Integer, default=20, nullable=False)
    last_stock_update = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    variant = relationship("ProductVariant", back_populates="inventory_records")
    warehouse = relationship("Warehouse")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    transaction_type = Column(String(50), nullable=False)  # purchase, sale, return, damage, adjustment, restock, transfer
    quantity = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    new_quantity = Column(Integer, nullable=False)
    reference_type = Column(String(50), nullable=True)  # order, return, adjustment, seed
    reference_id = Column(String(100), nullable=True)
    reason = Column(String(255), nullable=True)
    performed_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


# =============================================================================
# 5. CARTS & WISHLISTS
# =============================================================================
class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    session_id = Column(String(150), nullable=True, index=True)
    subtotal = Column(Numeric(12, 2), default=0.0, nullable=False)
    discount = Column(Numeric(12, 2), default=0.0, nullable=False)
    tax = Column(Numeric(12, 2), default=0.0, nullable=False)
    shipping_fee = Column(Numeric(12, 2), default=0.0, nullable=False)
    total = Column(Numeric(12, 2), default=0.0, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="active")  # active, converted, abandoned
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0.0)
    subtotal = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")


class Wishlist(Base):
    __tablename__ = "wishlists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), default="My Wishlist")
    is_default = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="wishlists")
    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    added_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    wishlist = relationship("Wishlist", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")


# =============================================================================
# 6. ORDERS, PAYMENTS & SHIPMENTS
# =============================================================================
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    billing_address_id = Column(Integer, ForeignKey("customer_addresses.id", ondelete="SET NULL"), nullable=True)
    shipping_address_id = Column(Integer, ForeignKey("customer_addresses.id", ondelete="SET NULL"), nullable=True)

    subtotal = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0.0)
    coupon_discount = Column(Numeric(12, 2), default=0.0)
    tax = Column(Numeric(12, 2), default=0.0)
    shipping_fee = Column(Numeric(12, 2), default=0.0)
    gift_wrap_fee = Column(Numeric(12, 2), default=0.0)
    total = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="INR")

    payment_status = Column(String(50), default="pending")  # pending, paid, failed, refunded
    order_status = Column(String(50), default="pending", index=True)  # pending, confirmed, processing, packed, shipped, out_for_delivery, delivered, cancelled, returned, refunded
    fulfillment_status = Column(String(50), default="unfulfilled")
    shipping_status = Column(String(50), default="pending")
    tracking_number = Column(String(150), nullable=True, index=True)
    carrier = Column(String(100), default="BlueDart / Delhivery")
    estimated_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    customer_notes = Column(Text, nullable=True)

    placed_at = Column(DateTime(timezone=True), default=utc_now)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order")
    shipments = relationship("Shipment", back_populates="order")
    shipping_address = relationship("CustomerAddress", foreign_keys=[shipping_address_id])
    billing_address = relationship("CustomerAddress", foreign_keys=[billing_address_id])


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True)
    product_name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=False)
    size = Column(String(20), nullable=False)
    color = Column(String(50), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0.0)
    tax = Column(Numeric(12, 2), default=0.0)
    subtotal = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    payment_method = Column(String(50), nullable=False)  # UPI, Credit Card, Debit Card, Net Banking, Wallet, Cash on Delivery
    transaction_id = Column(String(150), unique=True, nullable=True, index=True)
    gateway = Column(String(50), default="Razorpay")  # Razorpay, Stripe, Mock
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="completed")  # initiated, pending, completed, failed, refunded
    payment_date = Column(DateTime(timezone=True), default=utc_now)
    refund_amount = Column(Numeric(12, 2), default=0.0)
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    gateway_response = Column(JSONType, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    order = relationship("Order", back_populates="payments")


class ShippingMethod(Base):
    __tablename__ = "shipping_methods"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # Standard Delivery, Express Air, Next Day
    carrier = Column(String(100), default="BlueDart / Delhivery")
    description = Column(String(255), nullable=True)
    estimated_days = Column(Integer, default=3)
    price = Column(Numeric(12, 2), default=0.0)
    free_shipping_threshold = Column(Numeric(12, 2), default=1500.0)
    tracking_supported = Column(Boolean, default=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="SET NULL"), nullable=True)
    carrier = Column(String(100), default="Delhivery")
    tracking_number = Column(String(150), nullable=False, index=True)
    shipping_method_id = Column(Integer, ForeignKey("shipping_methods.id", ondelete="SET NULL"), nullable=True)
    package_weight = Column(Float, default=800.0)
    package_length = Column(Float, default=30.0)
    package_width = Column(Float, default=20.0)
    package_height = Column(Float, default=12.0)
    shipping_cost = Column(Numeric(12, 2), default=120.0)
    status = Column(String(50), default="shipped")  # manifest, picked_up, in_transit, out_for_delivery, delivered, returned
    shipped_at = Column(DateTime(timezone=True), default=utc_now)
    estimated_delivery = Column(Date, nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    order = relationship("Order", back_populates="shipments")


# =============================================================================
# 7. COUPONS, REVIEWS, RETURNS & REFUNDS
# =============================================================================
class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    discount_type = Column(String(20), default="percentage")  # percentage, fixed, free_shipping
    discount_value = Column(Float, nullable=False)
    minimum_order_amount = Column(Numeric(12, 2), default=0.0)
    maximum_discount = Column(Numeric(12, 2), nullable=True)
    usage_limit = Column(Integer, default=1000)
    usage_count = Column(Integer, default=0)
    per_user_limit = Column(Integer, default=1)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    applicable_category_id = Column(Integer, nullable=True)
    applicable_product_id = Column(Integer, nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class CouponUsage(Base):
    __tablename__ = "coupon_usage"

    id = Column(Integer, primary_key=True, autoincrement=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    discount_amount = Column(Numeric(12, 2), nullable=False)
    used_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    rating = Column(Integer, nullable=False)  # 1 to 5
    title = Column(String(255), nullable=True)
    review_text = Column(Text, nullable=False)
    verified_purchase = Column(Boolean, default=True)
    helpful_count = Column(Integer, default=0)
    status = Column(String(50), default="approved")  # pending, approved, rejected
    admin_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    images = relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan")


class ReviewImage(Base):
    __tablename__ = "review_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    review = relationship("Review", back_populates="images")


class ReviewHelpfulness(Base):
    __tablename__ = "review_helpfulness"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_helpful = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_helpfulness_user"),
    )


class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    return_number = Column(String(100), unique=True, nullable=False, index=True)
    reason = Column(String(100), nullable=False)  # wrong_size, damaged, defective, wrong_product, not_satisfied, changed_mind, other
    description = Column(Text, nullable=True)
    condition = Column(String(100), default="unworn_with_tags")
    return_type = Column(String(50), default="refund")  # refund, replacement, store_credit
    requested_date = Column(DateTime(timezone=True), default=utc_now)
    approved_date = Column(DateTime(timezone=True), nullable=True)
    pickup_date = Column(Date, nullable=True)
    received_date = Column(Date, nullable=True)
    status = Column(String(50), default="requested")  # requested, approved, picked_up, received, inspected, completed, rejected
    refund_amount = Column(Numeric(12, 2), nullable=False)
    refund_status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    return_id = Column(Integer, ForeignKey("returns.id", ondelete="SET NULL"), nullable=True)
    refund_transaction_id = Column(String(150), unique=True, nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    reason = Column(String(255), nullable=True)
    status = Column(String(50), default="processed")
    processed_at = Column(DateTime(timezone=True), default=utc_now)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


# =============================================================================
# 8. ENGAGEMENT, SEARCH, CMS & AUDIT
# =============================================================================
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="order_update")
    channel = Column(String(50), default="in_app")  # email, sms, push, in_app
    read_status = Column(Boolean, default=False)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(String(100), nullable=True)
    sent_at = Column(DateTime(timezone=True), default=utc_now)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class ProductQuestion(Base):
    __tablename__ = "product_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    status = Column(String(50), default="answered")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    product = relationship("Product", back_populates="questions")
    answers = relationship("ProductAnswer", back_populates="question", cascade="all, delete-orphan")


class ProductAnswer(Base):
    __tablename__ = "product_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("product_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    answer = Column(Text, nullable=False)
    is_admin_answer = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    question = relationship("ProductQuestion", back_populates="answers")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    session_id = Column(String(150), nullable=True)
    search_query = Column(String(255), nullable=False)
    results_count = Column(Integer, default=0)
    searched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class RecentlyViewed(Base):
    __tablename__ = "recently_viewed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    viewed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class ProductComparison(Base):
    __tablename__ = "product_comparison"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    subtitle = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=False)
    mobile_image_url = Column(String(500), nullable=True)
    button_text = Column(String(100), default="Shop Now")
    button_url = Column(String(500), default="/shop")
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    display_order = Column(Integer, default=1)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class HomepageSection(Base):
    __tablename__ = "homepage_sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    subtitle = Column(String(255), nullable=True)
    section_type = Column(String(50), nullable=False)  # hero, featured_products, new_arrivals, best_sellers, categories, offers, brands, testimonials, blog
    display_order = Column(Integer, default=1)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, nullable=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    excerpt = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    cover_image = Column(String(500), nullable=True)
    category = Column(String(100), default="Footwear Guide")
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(500), nullable=True)
    status = Column(String(50), default="published")
    published_at = Column(DateTime(timezone=True), default=utc_now)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(50), default="medium")  # low, medium, high, urgent
    status = Column(String(50), default="open")  # open, in_progress, resolved, closed
    assigned_to = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, nullable=False, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=True)
    old_values = Column(JSONType, nullable=True)
    new_values = Column(JSONType, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
