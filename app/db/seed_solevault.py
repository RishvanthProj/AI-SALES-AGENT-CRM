import logging
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.db.solevault_models import (
    Base,
    User,
    CustomerAddress,
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVideo,
    ProductVariant,
    ProductColor,
    ProductSize,
    ProductFeature,
    ProductTag,
    ProductTagMapping,
    Warehouse,
    Inventory,
    InventoryTransaction,
    Cart,
    CartItem,
    Wishlist,
    WishlistItem,
    Order,
    OrderItem,
    Payment,
    Coupon,
    CouponUsage,
    Review,
    ReviewImage,
    ReviewHelpfulness,
    Return,
    Refund,
    ShippingMethod,
    Shipment,
    Notification,
    ProductQuestion,
    ProductAnswer,
    Banner,
    HomepageSection,
    BlogPost,
    SupportTicket,
    AdminAuditLog
)

logger = logging.getLogger("solevault_seed")


def _now():
    return datetime.now(timezone.utc)


async def seed_solevault_database(session: AsyncSession) -> Dict[str, int]:
    """
    Seeds the SOLEVAULT relational database with comprehensive demo dataset:
    - 5 Brands
    - 20 Shoe Categories (Running, Walking, Sports, Training, Sneakers, etc.)
    - 3 Warehouses
    - 10 Users & Addresses
    - 25 Detailed Shoe Products (70+ fields each)
    - 75 Product Images & 25 Videos
    - 10 Colors & 30 Size Systems (UK 3-12, US 4-13, EU 36-45)
    - 300+ Product Variants & Inventory records
    - 100+ Product Features & 12 Product Tags
    - Shipping Methods, Coupons, Orders, Payments, Reviews, Returns, Banners, Blog Posts
    """
    # Check if products already exist
    existing = await session.scalar(select(func.count(Product.id)))
    if existing and existing >= 20:
        logger.info("SOLEVAULT database already contains >= 20 products. Skipping seed.")
        return {"products": existing}

    logger.info("Seeding SOLEVAULT database with comprehensive footwear dataset...")

    # 1. BRANDS
    brands_data = [
        {"id": 1, "name": "AeroSprint", "slug": "aerosprint", "description": "High-performance marathon and sprint footwear engineered with responsive air cushions.", "logo_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=200", "website_url": "https://aerosprint.solevault.com"},
        {"id": 2, "name": "UrbanFlex", "slug": "urbanflex", "description": "Contemporary urban lifestyle sneakers crafted with cloud-like memory foam footbeds.", "logo_url": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=200", "website_url": "https://urbanflex.solevault.com"},
        {"id": 3, "name": "TerraGrip", "slug": "terragrip", "description": "Rugged outdoor, trail, and mountaineering footwear built with extreme all-weather traction.", "logo_url": "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=200", "website_url": "https://terragrip.solevault.com"},
        {"id": 4, "name": "CourtRush", "slug": "courtrush", "description": "Professional indoor and hard-court basketball, tennis, and training performance shoes.", "logo_url": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=200", "website_url": "https://courtrush.solevault.com"},
        {"id": 5, "name": "HeritageWalk", "slug": "heritagewalk", "description": "Artisanal handcrafted leather formals, loafers, and traditional Indian ethnic footwear.", "logo_url": "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=200", "website_url": "https://heritagewalk.solevault.com"},
    ]
    for b in brands_data:
        brand = Brand(
            id=b["id"],
            name=b["name"],
            slug=b["slug"],
            description=b["description"],
            logo_url=b["logo_url"],
            banner_url=f"https://images.unsplash.com/photo-1556906781-9a412961c28c?w=1200",
            website_url=b["website_url"],
            status="active"
        )
        session.add(brand)

    # 2. CATEGORIES (20 Required Categories)
    categories_data = [
        (1, "Running Shoes", "running-shoes", "Engineered for speed, energy return, and long-distance comfort.", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600"),
        (2, "Walking Shoes", "walking-shoes", "Featherlight everyday walkers with ergonomic arch support.", "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600"),
        (3, "Sports Shoes", "sports-shoes", "Multi-sport athletic shoes for agility, stability, and speed.", "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=600"),
        (4, "Training Shoes", "training-shoes", "Gym and cross-training footwear with reinforced stability frames.", "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600"),
        (5, "Sneakers", "sneakers", "Iconic street-ready lifestyle sneakers with premium finishes.", "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=600"),
        (6, "Basketball Shoes", "basketball-shoes", "High-top court shoes with maximum ankle lock and rebound.", "https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=600"),
        (7, "Football Shoes", "football-shoes", "Firm ground studs with precise ball touch and grip control.", "https://images.unsplash.com/photo-1511556532299-8f662fc26c06?w=600"),
        (8, "Trekking Shoes", "trekking-shoes", "Heavy-duty mountain terrain footwear with waterproof shield.", "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=600"),
        (9, "Hiking Shoes", "hiking-shoes", "All-weather trail shoes with deep lugged rubber outsoles.", "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=600"),
        (10, "Formal Shoes", "formal-shoes", "Handcrafted Italian and Oxford leather shoes for boardroom elegance.", "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600"),
        (11, "Casual Shoes", "casual-shoes", "Effortless everyday footwear blending style and all-day ease.", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=600"),
        (12, "Sandals", "sandals", "Breathable, open-toe sandals with contoured orthotic footbeds.", "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=600"),
        (13, "Slippers", "slippers", "Ultra-soft indoor/outdoor EVA slides and memory foam slippers.", "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=600"),
        (14, "Kids Shoes", "kids-shoes", "Play-proof, ultra-flexible shoes designed for growing feet.", "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=600"),
        (15, "School Shoes", "school-shoes", "Reinforced scuff-resistant uniform shoes built for durability.", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600"),
        (16, "Boots", "boots", "Tactical and chelsea leather boots with heavy-duty weather armor.", "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=600"),
        (17, "Slip-On Shoes", "slip-on-shoes", "Lace-free convenience with stretch collar and instant cushioning.", "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=600"),
        (18, "Ethnic / Traditional Footwear", "ethnic-traditional-footwear", "Hand-stitched leather Juttis, Mojaris, and Kolhapuris with royal comfort.", "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600"),
        (19, "Lifestyle Shoes", "lifestyle-shoes", "Fashion-forward retro runners and statement daily trainers.", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600"),
        (20, "Limited Edition Shoes", "limited-edition-shoes", "Exclusive collector editions featuring carbon plates and responsive foam.", "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600"),
    ]
    for cat_id, name, slug, desc, img in categories_data:
        cat = Category(
            id=cat_id,
            parent_category_id=None,
            name=name,
            slug=slug,
            description=desc,
            image_url=img,
            banner_url=img,
            meta_title=f"Shop {name} | SOLEVAULT Footwear",
            meta_description=f"Explore premium {name} from SOLEVAULT. Free shipping on orders over ₹1,500.",
            display_order=cat_id,
            status="active"
        )
        session.add(cat)

    # 3. WAREHOUSES
    warehouses_data = [
        (1, "Chennai Central Warehouse", "CHN-01", "100 GST Road, Guindy", "Chennai", "Tamil Nadu", "600032", "Arun Kumar", "+919800000001"),
        (2, "Bengaluru Logistics Hub", "BLR-01", "45 Electronic City Phase 1", "Bengaluru", "Karnataka", "560100", "Meena Rao", "+919800000002"),
        (3, "Hyderabad Fulfillment Center", "HYD-01", "12 HITEC City Main Rd", "Hyderabad", "Telangana", "500081", "Rahul Das", "+919800000003"),
    ]
    for w_id, name, code, addr, city, state, pin, mgr, phone in warehouses_data:
        wh = Warehouse(
            id=w_id,
            name=name,
            code=code,
            address=addr,
            city=city,
            state=state,
            country="India",
            postal_code=pin,
            manager_name=mgr,
            manager_phone=phone,
            status="active"
        )
        session.add(wh)

    # 4. USERS & ADDRESSES
    users_data = [
        (1, "Rishvanth", "Kumar", "rishvanth@solevault.com", "+919876543210", "admin", "male", "ta"),
        (2, "Ananya", "Sharma", "ananya@example.com", "+919876543211", "customer", "female", "en"),
        (3, "Karthik", "Raja", "karthik@example.com", "+919876543212", "customer", "male", "ta"),
        (4, "Priya", "Nair", "priya@example.com", "+919876543213", "customer", "female", "en"),
        (5, "Vikram", "Reddy", "vikram@example.com", "+919876543214", "customer", "male", "en"),
        (6, "Sneha", "Patel", "sneha@example.com", "+919876543215", "customer", "female", "en"),
        (7, "Suresh", "Mani", "suresh@example.com", "+919876543216", "inventory_manager", "male", "ta"),
        (8, "Deepa", "Sundaram", "deepa@example.com", "+919876543217", "support_agent", "female", "ta"),
        (9, "Arjun", "Menon", "arjun@example.com", "+919876543218", "customer", "male", "en"),
        (10, "Kavita", "Iyer", "kavita@example.com", "+919876543219", "customer", "female", "ta"),
    ]
    for u_id, fn, ln, email, phone, role, gender, lang in users_data:
        user = User(
            id=u_id,
            first_name=fn,
            last_name=ln,
            full_name=f"{fn} {ln}",
            email=email,
            phone=phone,
            password_hash="$2b$12$e8Y6bFp0mU4WbU8nK.N5.eO1v0Q.8YnB5s2A9wX7v6V5u4T3s2R1q",  # bcrypt hash of 'SoleVault@2026'
            gender=gender,
            role=role,
            status="active",
            email_verified=True,
            phone_verified=True,
            preferred_language=lang,
            preferred_currency="INR"
        )
        session.add(user)

        addr = CustomerAddress(
            id=u_id,
            user_id=u_id,
            address_type="home" if u_id % 2 == 1 else "office",
            recipient_name=f"{fn} {ln}",
            phone=phone,
            address_line_1=f"#{10 + u_id}, 4th Cross, Green Valley",
            address_line_2="Anna Nagar West",
            landmark="Near Metro Station",
            city="Chennai" if u_id in [1, 3, 7, 8] else ("Bengaluru" if u_id in [2, 5, 9] else "Hyderabad"),
            state="Tamil Nadu" if u_id in [1, 3, 7, 8] else ("Karnataka" if u_id in [2, 5, 9] else "Telangana"),
            country="India",
            postal_code=f"60000{u_id}",
            is_default_shipping=True,
            is_default_billing=True
        )
        session.add(addr)

    # 5. PRODUCT COLORS & SIZES
    colors_data = [
        (1, "Obsidian Black", "1A1A1A"),
        (2, "Summit White", "FFFFFF"),
        (3, "Crimson Red", "DC2626"),
        (4, "Royal Navy Blue", "1E3A8A"),
        (5, "Forest Olive", "15803D"),
        (6, "Cool Grey", "64748B"),
        (7, "Desert Tan", "D97706"),
        (8, "Sunset Orange", "EA580C"),
        (9, "Electric Pink", "EC4899"),
        (10, "Metallic Silver", "94A3B8"),
    ]
    for c_id, name, hex_code in colors_data:
        session.add(ProductColor(id=c_id, name=name, hex_code=hex_code, image_url=f"https://placehold.co/40x40/{hex_code}/ffffff?text={name[:2]}"))

    for i, sz in enumerate([3, 4, 5, 6, 7, 8, 9, 10, 11, 12], start=1):
        session.add(ProductSize(id=i, size=str(sz), size_system="UK", foot_length_cm=22.0 + (sz * 0.7), gender="Unisex"))
        session.add(ProductSize(id=i + 10, size=str(sz + 1), size_system="US", foot_length_cm=22.0 + (sz * 0.7), gender="Unisex"))
        session.add(ProductSize(id=i + 20, size=str(35 + sz), size_system="EU", foot_length_cm=22.0 + (sz * 0.7), gender="Unisex"))

    # 6. PRODUCT TAGS
    tags_data = ["running", "gym", "casual", "premium", "comfortable", "lightweight", "outdoor", "waterproof", "new", "sale", "bestseller", "limited-edition"]
    for t_id, tag_name in enumerate(tags_data, start=1):
        session.add(ProductTag(id=t_id, name=tag_name, slug=tag_name))

    # 7. 25 SHOE PRODUCTS (Covering all 20 categories + variations)
    products_master = [
        # (id, brand_id, category_id, name, slug, sku, price, mrp, color, tech, gender, weight, water_res, desc, img_primary, best_seller, featured, new_arr, lim_ed)
        (1, 1, 1, "AeroSprint X1", "aerosprint-x1", "SV-0001", 4999.0, 4999.0, "Black/Red", "Lightweight Foam + Air Cushion", "Unisex", 580.0, False, "Engineered for high-mileage road runners. Features proprietary dual-density ZoomAir pods and breathable mesh.", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800", False, True, True, False),
        (2, 2, 5, "UrbanFlex 200", "urbanflex-200", "SV-0002", 3499.0, 3499.0, "White/Grey", "Memory Foam Footbed", "Men", 630.0, False, "Sleek low-profile court sneakers with buttery leather overlays and responsive memory foam.", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800", True, False, False, False),
        (3, 3, 2, "LunaWalk Pro", "lunawalk-pro", "SV-0003", 2999.0, 2999.0, "Pink/White", "Comfort Mesh + Soft Cushion", "Women", 490.0, False, "Featherlight walking shoe engineered for morning fitness and all-day hospital/retail shifts.", "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800", False, False, False, False),
        (4, 4, 4, "TitanForce Elite", "titanforce-elite", "SV-0004", 4299.0, 4599.0, "Obsidian Black", "Stability Frame + Grip Outsole", "Men", 740.0, True, "Cross-training powerhouse with a flat wide base for heavy squats, deadlifts, and rope climbs.", "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800", False, False, False, False),
        (5, 5, 6, "CourtRush 7", "courtrush-7", "SV-0005", 5999.0, 5999.0, "Royal Navy/White", "High-Rebound Cushion + Ankle Lock", "Men", 790.0, False, "Explosive basketball performance kicks with herringbone multidirectional grip and TPU torsional plate.", "https://images.unsplash.com/photo-1579338559194-a162d19bf842?w=800", True, True, False, False),
        (6, 1, 7, "GoalStrike FG", "goalstrike-fg", "SV-0006", 4299.0, 4299.0, "Black/Gold", "Grip Control Sole + Micro-Textured Upper", "Unisex", 510.0, False, "Firm ground football cleats offering surgical passing precision and acceleration.", "https://images.unsplash.com/photo-1511556532299-8f662fc26c06?w=800", False, False, False, False),
        (7, 2, 8, "TerraGrip X", "terragrip-x", "SV-0007", 5499.0, 5499.0, "Olive/Black", "Multi-Terrain Lugged Grip + Kevlar Upper", "Unisex", 780.0, True, "Conquer Himalayan trails and rainy mountain passes with heavy-duty rock protection plates.", "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=800", False, False, True, False),
        (8, 3, 9, "SummitGuard Pro", "summitguard-pro", "SV-0008", 6199.0, 6499.0, "Brown/Black", "Waterproof Gore-Shield + Shock Absorber", "Men", 820.0, True, "All-weather mountaineering and hiking boot built for extreme wet conditions and rocky trails.", "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800", False, False, False, False),
        (9, 4, 10, "Executive Prime", "executive-prime", "SV-0009", 3799.0, 3799.0, "Rich Tan Brown", "Full Grain Leather + Ergonomic Arch", "Men", 680.0, False, "Classic Derby formal shoes crafted from premium bovine leather with anti-fatigue latex insole.", "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800", False, False, False, False),
        (10, 5, 17, "ClassicEase", "classicease", "SV-0010", 2699.0, 2699.0, "Warm Beige", "Memory Foam Slip-On Cushion", "Women", 430.0, False, "Ultra-convenient slip-on loafers with elastic stretch gore and cloud memory foam footbed.", "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=800", False, True, False, False),
        (11, 1, 19, "StreetNova", "streetnova", "SV-0011", 3999.0, 3999.0, "Cool Grey/White", "Cloud Cushion + Chunky Outsole", "Unisex", 660.0, False, "Retro runner-inspired lifestyle sneaker with chunky sculpted midsole and reflective 3M accents.", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800", True, False, False, False),
        (12, 2, 13, "ComfyCloud", "comfycloud", "SV-0012", 699.0, 999.0, "Matte Black", "Soft Injection EVA Cushion", "Unisex", 320.0, True, "Waterproof recovery slides engineered for post-workout foot relaxation and casual poolside wear.", "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=800", False, False, False, False),
        (13, 3, 12, "BeachFlow", "beachflow", "SV-0013", 1499.0, 1499.0, "Royal Blue", "Anti-Slip Footbed + Hydrophobic Straps", "Women", 380.0, True, "Quick-drying adventure sandals with adjustable velcro webbing and shock-absorbing EVA sole.", "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=800", False, False, False, False),
        (14, 4, 14, "JuniorSprint", "juniorsprint", "SV-0014", 1899.0, 1899.0, "Electric Blue/Orange", "Flexible Phylon Sole + Velcro Lock", "Kids", 340.0, False, "Playground-tested running shoe designed for school sports day, running, and active play.", "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=800", False, False, False, False),
        (15, 5, 15, "SchoolStep Max", "schoolstep-max", "SV-0015", 1399.0, 1399.0, "Pitch Black", "Durable Scuff-Resistant EVA Sole", "Kids", 410.0, False, "All-day school uniform shoe engineered with reinforced toe bumper and breathable mesh lining.", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=800", False, False, False, False),
        (16, 1, 16, "IronTrail Boot", "irontrail-boot", "SV-0016", 6699.0, 6999.0, "Dark Walnut Brown", "Heavy-Duty Vibram-Style Grip + Oil Resistance", "Men", 950.0, True, "Handcrafted rugged work boots featuring Goodyear welt construction and steel shank support.", "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800", False, False, False, False),
        (17, 2, 3, "DailyDash", "dailydash", "SV-0017", 3299.0, 3299.0, "Purple/White", "Breathable Jacquard Mesh + Air Unit", "Women", 520.0, False, "Versatile sports shoe perfect for treadmill runs, badminton, and outdoor evening jogs.", "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800", False, False, False, False),
        (18, 3, 18, "HeritageWalk", "heritagewalk", "SV-0018", 2499.0, 2499.0, "Tan Brown", "Soft Hand-Stitched Leather Footbed", "Men", 460.0, False, "Royal traditional handcrafted Mojari with velvet insole lining and genuine leather sole.", "https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=800", False, False, False, False),
        (19, 4, 11, "StreetVolt", "streetvolt", "SV-0019", 4499.0, 4499.0, "Black/White", "EVA Cushion + Suede Accents", "Men", 670.0, False, "Skate-inspired streetwear sneakers with padded collar and high-abrasion vulcanized sole.", "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=800", True, False, False, False),
        (20, 5, 20, "Velocity One Limited", "velocity-one-limited", "SV-0020", 8699.0, 8999.0, "Metallic Silver/Black", "Carbon Fiber Plate + HyperBurst Foam", "Unisex", 490.0, False, "Elite racing super-shoe featuring a full-length curved carbon fiber propulsion plate.", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800", False, True, False, True),
        (21, 1, 2, "FlexStep Air", "flexstep-air", "SV-0021", 2799.0, 2799.0, "Navy/White", "Air Comfort Foam + Elastic Mesh", "Women", 440.0, False, "Ultra-cushioned recovery walker with slip-on collar and anti-odor bamboo insole.", "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800", False, False, False, False),
        (22, 2, 19, "UrbanBeat 90", "urbanbeat-90", "SV-0022", 3199.0, 3199.0, "Forest Green/White", "Responsive EVA + Gum Rubber Bottom", "Unisex", 610.0, False, "Vintage 90s court silhouette with retro color blocking and breathable perforated toe box.", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800", False, False, False, False),
        (23, 3, 8, "TrailCore 4", "trailcore-4", "SV-0023", 5799.0, 5799.0, "Grey/Electric Orange", "Rugged Grip System + Mud Guard", "Men", 810.0, True, "Technical trail shoe with aggressive 6mm lugs and debris-shedding gusseted tongue.", "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=800", False, False, False, False),
        (24, 4, 3, "CourtLite", "courtlite", "SV-0024", 3599.0, 3899.0, "White/Cyan Blue", "Impact Absorbing Midsole + Non-Marking Sole", "Unisex", 590.0, False, "Non-marking indoor court footwear approved for badminton, squash, and volleyball.", "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800", False, False, False, False),
        (25, 5, 14, "KidzGlow", "kidzglow", "SV-0025", 1599.0, 1599.0, "Crimson Red/Black", "Flexible Glow Sole + Impact Shock Protection", "Kids", 310.0, False, "Fun light-up athletic shoe for kids featuring shock-absorbing sole and easy pull tabs.", "https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=800", False, False, False, False),
    ]

    variant_counter = 1
    image_counter = 1
    inventory_counter = 1

    for (p_id, b_id, c_id, name, slug, sku, sale_price, mrp, color_name, tech, gender, weight, water_res, desc, img_p, best_s, feat, new_a, lim_e) in products_master:
        disc_pct = round(((mrp - sale_price) / mrp) * 100, 2) if mrp > sale_price else 0.0

        p = Product(
            id=p_id,
            brand_id=b_id,
            category_id=c_id,
            subcategory_id=c_id,
            name=name,
            slug=slug,
            sku=sku,
            product_code=f"SVP-2026-{p_id:04d}",
            short_description=f"{name} — {tech}.",
            long_description=desc,
            material="Synthetic / Engineered Mesh",
            upper_material="Engineered Breathable Mesh" if "Mesh" in desc else "Premium Synthetic Leather",
            lining_material="Breathable Textile",
            insole_material="Memory Foam / OrthoLite",
            outsole_material="High-Traction Rubber / EVA",
            sole_type="EVA / Rubber Compound",
            closure_type="Slip-On" if c_id in [10, 12, 13, 17, 18, 21] else "Lace-Up",
            heel_type="Low-Profile Flat",
            toe_shape="Round Toe",
            shoe_width="Regular Fit",
            shoe_height="Low-Top" if c_id not in [6, 8, 9, 16] else ("Mid-Top" if c_id in [6, 8] else "High-Top"),
            weight=weight,
            heel_height=10.0,
            platform_height=3.0,
            water_resistant=water_res,
            waterproof=water_res and c_id in [8, 9, 16],
            breathable=True,
            shock_absorption="High" if "Cushion" in tech or "Air" in tech else "Medium",
            arch_support="Ergonomic Arch Support",
            cushioning_level="Maximum" if lim_e or "Air" in tech else "High",
            flexibility_level="High",
            traction_level="Maximum" if c_id in [7, 8, 9, 16, 23] else "High",
            durability_rating=4.7,
            comfort_rating=4.8,
            occasion="Sports" if c_id in [1, 3, 4, 6, 7, 24] else ("Outdoor" if c_id in [8, 9, 16, 23] else ("Formal" if c_id == 10 else "Casual")),
            sport="Running" if c_id == 1 else ("Basketball" if c_id == 6 else ("Football" if c_id == 7 else ("Trekking" if c_id in [8, 9, 23] else None))),
            gender=gender,
            age_group="Kids" if c_id in [14, 15, 25] else "Adult",
            season="All Season",
            collection="Performance 2026" if c_id in [1, 6, 7, 20] else "Urban Street 2026",
            style="Athletic / Streetwear",
            fit_type="True to Size (Regular)",
            size_type="UK",
            country_of_origin="India",
            manufacturer="SOLEVAULT Footwear Labs India Ltd.",
            manufacturer_part_number=f"MFG-{p_id:04d}",
            warranty_period="6 Months Manufacturing Warranty",
            care_instructions="Wipe gently with damp cloth. Air dry away from direct sunlight. Do not machine wash.",
            features=f"{tech}; Ergonomic footbed; Anti-slip grip outsole.",
            technology=tech,
            certifications="ISO 9001:2015 Footwear Standards",
            sustainability_information="Crafted with up to 30% recycled textile and eco-friendly water-based adhesives.",
            available_quantity=50,
            reserved_quantity=2,
            low_stock_threshold=5,
            base_price=Decimal(str(sale_price)),
            sale_price=Decimal(str(sale_price)),
            cost_price=Decimal(str(round(sale_price * 0.45, 2))),
            mrp=Decimal(str(mrp)),
            tax_rate=18.0,
            discount_percentage=disc_pct,
            currency="INR",
            status="active",
            visibility=True,
            featured=feat,
            best_seller=best_s,
            new_arrival=new_a,
            limited_edition=lim_e,
            rating_average=4.5 + ((p_id % 5) * 0.1),
            rating_count=30 + (p_id * 12),
            view_count=150 + (p_id * 45),
            purchase_count=25 + (p_id * 8),
            wishlist_count=40 + (p_id * 15),
            meta_title=f"{name} - Buy Online | SOLEVAULT",
            meta_description=f"Shop {name} with {tech}. 7-day hassle-free returns & COD available across India.",
            meta_keywords=f"{name}, {gender} shoes, {tech}, SOLEVAULT footwear",
            canonical_url=f"https://solevault.com/products/{slug}"
        )
        session.add(p)

        # Images (3 per shoe)
        views = [("front", img_p), ("side", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"), ("top", "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800")]
        for idx, (img_type, url) in enumerate(views, start=1):
            session.add(ProductImage(
                id=image_counter,
                product_id=p_id,
                image_url=url,
                thumbnail_url=url,
                alt_text=f"{name} {img_type} view",
                image_type=img_type,
                display_order=idx,
                is_primary=(idx == 1)
            ))
            image_counter += 1

        # Videos
        session.add(ProductVideo(
            id=p_id,
            product_id=p_id,
            video_url="https://assets.mixkit.co/videos/preview/mixkit-running-shoes-in-a-sports-store-42589-large.mp4",
            thumbnail_url=img_p,
            title=f"{name} 360 Feature Demonstration",
            description=f"Watch the {name} with {tech} in action.",
            duration=35
        ))

        # Features
        features_list = [
            ("Technology", tech),
            ("Upper Material", p.upper_material),
            ("Sole Type", p.sole_type),
            ("Closure", p.closure_type),
            ("Weight", f"{weight:.0f} grams"),
            ("Water Resistance", "Yes" if water_res else "Standard Splash Proof"),
        ]
        for f_idx, (f_name, f_val) in enumerate(features_list, start=1):
            session.add(ProductFeature(
                product_id=p_id,
                feature_name=f_name,
                feature_value=f_val,
                display_order=f_idx
            ))

        # Tag Mappings
        session.add(ProductTagMapping(product_id=p_id, tag_id=1 if c_id in [1, 3] else (3 if c_id in [5, 11] else 4)))
        session.add(ProductTagMapping(product_id=p_id, tag_id=11 if best_s else (9 if new_a else (12 if lim_e else 5))))

        # Variants (3 Colors x 4 Sizes = 12 variants per shoe)
        colors_to_use = [("Black", "1A1A1A"), ("White", "FFFFFF"), ("Navy", "1E3A8A")] if p_id % 2 == 0 else [("Black", "1A1A1A"), ("Red", "DC2626"), ("Grey", "64748B")]
        sizes_to_use = ["6", "7", "8", "9", "10", "11"] if c_id not in [14, 15, 25] else ["3", "4", "5", "6"]

        for color_title, color_hex in colors_to_use:
            for size_val in sizes_to_use:
                var_sku = f"{sku}-{color_title[:2].upper()}-{size_val}"
                stock = 0 if (p_id == 4 and size_val == "11") else (3 if (p_id == 2 and size_val == "9") else 12)
                
                variant = ProductVariant(
                    id=variant_counter,
                    product_id=p_id,
                    sku=var_sku,
                    barcode=f"8902026{variant_counter:06d}",
                    color=color_title,
                    color_code=color_hex,
                    size=size_val,
                    size_system="UK",
                    width="Regular",
                    gender=gender,
                    stock_quantity=stock,
                    reserved_quantity=0,
                    available_quantity=stock,
                    price=Decimal(str(sale_price)),
                    sale_price=Decimal(str(sale_price)),
                    mrp=Decimal(str(mrp)),
                    weight=weight,
                    image_url=img_p,
                    status="active"
                )
                session.add(variant)

                # Inventory across warehouses
                wh_id = ((variant_counter % 3) + 1)
                session.add(Inventory(
                    id=inventory_counter,
                    product_id=p_id,
                    variant_id=variant_counter,
                    warehouse_id=wh_id,
                    quantity=stock,
                    reserved_quantity=0,
                    available_quantity=stock,
                    damaged_quantity=0,
                    incoming_quantity=10,
                    reorder_level=5,
                    reorder_quantity=20,
                    last_stock_update=date.today()
                ))
                inventory_counter += 1
                variant_counter += 1

    # 8. SHIPPING METHODS
    shipping_methods = [
        (1, "Standard Express Ground", "BlueDart / Delhivery", "Fast pan-India delivery within 3-5 business days.", 3, Decimal("0.0"), Decimal("1500.0")),
        (2, "Air Priority Superfast", "BlueDart Air", "Next day air shipping to all Tier-1 Indian metros.", 1, Decimal("150.0"), Decimal("5000.0")),
    ]
    for sm_id, name, carrier, desc, days, price, thresh in shipping_methods:
        session.add(ShippingMethod(
            id=sm_id,
            name=name,
            carrier=carrier,
            description=desc,
            estimated_days=days,
            price=price,
            free_shipping_threshold=thresh,
            tracking_supported=True,
            status="active"
        ))

    # 9. COUPONS
    coupons_data = [
        (1, "STRIDE10", "Get 10% instant discount on orders above ₹1,999", "percentage", 10.0, Decimal("1999.0"), Decimal("1000.0")),
        (2, "WELCOME500", "Flat ₹500 discount for first-time shoe buyers", "fixed", 500.0, Decimal("2999.0"), Decimal("500.0")),
        (3, "SOLE15", "15% off on performance running & basketball shoes", "percentage", 15.0, Decimal("3999.0"), Decimal("1500.0")),
        (4, "FREESHIP", "Free priority express shipping across India", "free_shipping", 0.0, Decimal("0.0"), Decimal("150.0")),
    ]
    for cp_id, code, desc, d_type, d_val, min_amt, max_d in coupons_data:
        session.add(Coupon(
            id=cp_id,
            code=code,
            description=desc,
            discount_type=d_type,
            discount_value=d_val,
            minimum_order_amount=min_amt,
            maximum_discount=max_d,
            usage_limit=5000,
            usage_count=42,
            per_user_limit=2,
            status="active"
        ))

    # 10. ORDERS, PAYMENTS & REVIEWS
    orders_data = [
        (1, "SV-8942", 1, 1, Decimal("4999.0"), Decimal("499.90"), Decimal("4499.10"), "paid", "dispatched", "BLR-DEL-984210", "AeroSprint X1", 1, 1, "UK 8", "Black"),
        (2, "SV-9104", 2, 2, Decimal("3499.0"), Decimal("0.0"), Decimal("3499.0"), "paid", "delivered", "CHN-BLR-114092", "UrbanFlex 200", 2, 13, "UK 7", "White/Grey"),
        (3, "SV-9331", 3, 3, Decimal("5999.0"), Decimal("500.0"), Decimal("5499.0"), "paid", "processing", "HYD-CHN-559123", "CourtRush 7", 5, 53, "UK 9", "Navy"),
        (4, "SV-9440", 4, 4, Decimal("2999.0"), Decimal("0.0"), Decimal("2999.0"), "pending", "confirmed", "BLR-HYD-771234", "LunaWalk Pro", 3, 29, "UK 6", "Pink/White"),
    ]
    for o_id, o_num, u_id, a_id, sub, disc, tot, p_stat, o_stat, trk, p_name, prod_id, v_id, sz, col in orders_data:
        order = Order(
            id=o_id,
            order_number=o_num,
            user_id=u_id,
            billing_address_id=a_id,
            shipping_address_id=a_id,
            subtotal=sub,
            discount=disc,
            coupon_discount=disc,
            tax=Decimal(str(round(float(sub) * 0.18, 2))),
            shipping_fee=Decimal("0.0"),
            total=tot,
            currency="INR",
            payment_status=p_stat,
            order_status=o_stat,
            fulfillment_status="fulfilled" if o_stat in ["dispatched", "delivered"] else "unfulfilled",
            shipping_status="in_transit" if o_stat == "dispatched" else ("delivered" if o_stat == "delivered" else "pending"),
            tracking_number=trk,
            carrier="Delhivery Express",
            estimated_delivery_date=date.today(),
            placed_at=_now()
        )
        session.add(order)

        session.add(OrderItem(
            id=o_id,
            order_id=o_id,
            product_id=prod_id,
            variant_id=v_id,
            product_name=p_name,
            sku=f"SV-{prod_id:04d}-{sz}",
            size=sz,
            color=col,
            quantity=1,
            unit_price=sub,
            discount=disc,
            tax=Decimal(str(round(float(sub) * 0.18, 2))),
            subtotal=sub - disc,
            total=tot
        ))

        session.add(Payment(
            id=o_id,
            order_id=o_id,
            user_id=u_id,
            payment_method="UPI" if o_id % 2 == 1 else "Credit Card",
            transaction_id=f"TXN-UPI-{o_num}-2026",
            gateway="Razorpay",
            amount=tot,
            currency="INR",
            status="completed" if p_stat == "paid" else "pending"
        ))

    # 11. REVIEWS
    reviews_data = [
        (1, 1, 1, 5, "Best running shoe I've ever owned in India!", "The cushioning on the AeroSprint X1 is unbelievably bouncy. Tested on a 15km road marathon and zero heel pain. True to size!"),
        (2, 2, 2, 5, "Super aesthetic sneakers, looks premium", "Pairs great with relaxed denim and joggers. Memory foam footbed is super soft for daily office wear."),
        (3, 3, 4, 4, "Solid lifting shoe with heavy grip base", "TitanForce Elite locked my heels in place during 140kg squats. Very flat and stable."),
        (4, 4, 5, 5, "CourtRush 7 has unmatched ankle support!", "Played 3 competitive basketball matches in Chennai court. Traction stops on a dime!"),
        (5, 5, 7, 5, "Completed Kudremukh trek with zero slipping", "TerraGrip X handled heavy rains, wet rocks, and slippery mud effortlessly. Highly recommend!"),
    ]
    for r_id, u_id, p_id, rating, title, text_body in reviews_data:
        review = Review(
            id=r_id,
            user_id=u_id,
            product_id=p_id,
            order_id=r_id,
            rating=rating,
            title=title,
            review_text=text_body,
            verified_purchase=True,
            helpful_count=12 + (r_id * 4),
            status="approved"
        )
        session.add(review)

    # 12. BANNERS & BLOG POSTS
    session.add(Banner(
        id=1,
        title="Move Better. Live Better.",
        subtitle="Discover SOLEVAULT's high-performance running & lifestyle footwear engineered for champions.",
        image_url="https://images.unsplash.com/photo-1556906781-9a412961c28c?w=1600",
        mobile_image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800",
        button_text="Explore Collection",
        button_url="/shop"
    ))

    session.add(BlogPost(
        id=1,
        title="How to Choose the Right Running Shoe for Your Foot Type",
        slug="how-to-choose-running-shoes-foot-type",
        excerpt="Understanding pronation, arch height, and stack cushioning to prevent injuries and run faster.",
        content="Selecting the right running shoe is the single most important decision for runners...",
        cover_image="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800",
        category="Footwear Guide"
    ))

    session.add(SupportTicket(
        id=1,
        user_id=1,
        order_id=1,
        subject="Exchange request for size UK 9",
        description="I ordered size UK 8 but would like to swap for UK 9. Product is brand new with tags.",
        priority="medium",
        status="in_progress"
    ))

    await session.commit()
    logger.info("SOLEVAULT database seeding successfully completed!")
    return {
        "brands": len(brands_data),
        "categories": len(categories_data),
        "warehouses": len(warehouses_data),
        "users": len(users_data),
        "products": len(products_master),
        "variants": variant_counter - 1,
        "orders": len(orders_data),
        "coupons": len(coupons_data),
        "reviews": len(reviews_data)
    }
