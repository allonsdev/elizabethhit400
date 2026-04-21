"""
app/management/commands/seeder.py

Usage:
    python manage.py seeder           # seed (skip existing)
    python manage.py seeder --flush   # wipe all seeded tables first, then reseed
"""

import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import (          # ← adjust "app" if your app has a different name
    Supplier, Order, Delivery,
    SupplierReview, Complaint,
    SupplierPerformanceScore, SupplierSentiment,
    FastFoodBrand, CustomerProfile, Review,
    SentimentAnalysis, EngagementMetric,
    InventoryItem, MarketTrend, MarketIndicator,
    CompetitorMarketData, Benchmark, DecisionRecommendation,
)


def rand_date(start_days_ago=365, end_days_ago=0):
    delta = random.randint(end_days_ago, start_days_ago)
    return date.today() - timedelta(days=delta)


def rand_future_date(days_ahead=30):
    return date.today() + timedelta(days=random.randint(1, days_ahead))


# ── Static data ──────────────────────────────────────────────────────────────

SUPPLIERS_DATA = [
    {"supplier_code": "SUP-001", "name": "Irvine's Zimbabwe",    "company_name": "Irvine's (Pvt) Ltd",       "contact_person": "Tendai Moyo",       "email": "procurement@irvines.co.zw",  "phone": "+263 242 860 361", "location": "Harare, Zimbabwe"},
    {"supplier_code": "SUP-002", "name": "Colcom Foods",          "company_name": "Colcom Holdings Ltd",       "contact_person": "Chiedza Ncube",      "email": "supply@colcom.co.zw",        "phone": "+263 242 614 481", "location": "Harare, Zimbabwe"},
    {"supplier_code": "SUP-003", "name": "Dairibord Zimbabwe",    "company_name": "Dairibord Holdings Ltd",    "contact_person": "Farai Mutasa",       "email": "orders@dairibord.com",       "phone": "+263 242 667 026", "location": "Harare, Zimbabwe"},
    {"supplier_code": "SUP-004", "name": "National Foods",        "company_name": "National Foods Ltd",        "contact_person": "Kudzai Zvenyika",    "email": "logistics@natfoods.co.zw",   "phone": "+263 242 753 571", "location": "Harare, Zimbabwe"},
    {"supplier_code": "SUP-005", "name": "Lobels Bakeries",       "company_name": "Lobels (Pvt) Ltd",          "contact_person": "Rudo Chigwedere",    "email": "supply@lobels.co.zw",        "phone": "+263 242 446 229", "location": "Harare, Zimbabwe"},
    {"supplier_code": "SUP-006", "name": "Cairns Foods",          "company_name": "Cairns Holdings Ltd",       "contact_person": "Blessing Sibanda",   "email": "orders@cairns.co.zw",        "phone": "+263 292 882 361", "location": "Bulawayo, Zimbabwe"},
    {"supplier_code": "SUP-007", "name": "Tregers Distributors",  "company_name": "Tregers (Pvt) Ltd",         "contact_person": "Munyaradzi Dube",    "email": "info@tregers.co.zw",         "phone": "+263 242 770 330", "location": "Harare, Zimbabwe"},
    {"supplier_code": "SUP-008", "name": "Spar Zimbabwe",         "company_name": "Spar Zimbabwe (Pvt) Ltd",  "contact_person": "Nyasha Mlambo",      "email": "supply@sparzim.co.zw",       "phone": "+263 242 753 888", "location": "Harare, Zimbabwe"},
]

PRODUCTS = [
    ("Frozen Chicken Wings",    "Poultry",    "SKU-CHK-001", 25.50),
    ("Whole Chicken (1.5kg)",   "Poultry",    "SKU-CHK-002", 18.00),
    ("Pork Sausages 500g",      "Pork",       "SKU-PRK-001", 12.50),
    ("Full Cream Milk 2L",      "Dairy",      "SKU-DRY-001",  3.20),
    ("Cheddar Cheese 1kg",      "Dairy",      "SKU-DRY-002", 14.75),
    ("Maize Meal 10kg",         "Grain",      "SKU-GRN-001",  8.90),
    ("Bread Flour 2kg",         "Grain",      "SKU-GRN-002",  4.50),
    ("White Bread Loaf",        "Bakery",     "SKU-BKR-001",  1.80),
    ("Tomato Sauce 500ml",      "Condiments", "SKU-CND-001",  3.10),
    ("Cooking Oil 2L",          "Oils",       "SKU-OIL-001",  6.40),
    ("Baked Beans 410g",        "Canned",     "SKU-CAN-001",  2.20),
    ("Soft Drink 2L Coke",      "Beverages",  "SKU-BEV-001",  2.50),
    ("Mineral Water 500ml x24", "Beverages",  "SKU-BEV-002",  9.00),
    ("Paper Bags x500",         "Packaging",  "SKU-PKG-001",  7.80),
    ("Disposable Cups x200",    "Packaging",  "SKU-PKG-002",  5.60),
]

DRIVERS = [
    ("Tawanda Chirwa",  "ABZ 1234"),
    ("Simba Ndlovu",    "CAD 5678"),
    ("Grace Mhuri",     "HAR 9010"),
    ("Prosper Gumbo",   "BYO 3344"),
    ("Admire Chiweshe", "ZIM 6677"),
]

REVIEW_COMMENTS = [
    "Supplier consistently delivers on time and with excellent documentation.",
    "Communication could be improved — sometimes hard to reach during peak periods.",
    "Product quality has been outstanding, very pleased with consistency.",
    "Pricing is competitive compared to other Harare distributors.",
    "There have been occasional short deliveries but issues are resolved quickly.",
    "Driver is professional and arrives with all paperwork in order.",
    "Had a dispute over invoice amount but it was handled within 2 days.",
    "One of our most reliable suppliers — highly recommended.",
]

COMPLAINT_DESCS = [
    "Delivered expired products — best-before date already passed on arrival.",
    "Short delivery: ordered 200 units, only 160 received.",
    "Damaged packaging on chicken shipment, products unusable.",
    "Driver was rude and refused to offload at designated bay.",
    "Invoice amount did not match agreed purchase order price.",
    "No delivery note provided — failed audit.",
    "Delivery was 5 days late causing stock-out.",
]

SENTIMENTS = [
    ("Positive", 0.88, "Great delivery experience, products were fresh and on time."),
    ("Positive", 0.82, "Very professional team, always communicate delays in advance."),
    ("Neutral",  0.51, "Average service, nothing exceptional but nothing bad either."),
    ("Negative", 0.73, "Disappointed with the damaged goods and lack of accountability."),
    ("Negative", 0.68, "Late delivery caused us to run out of stock over a weekend."),
    ("Positive", 0.91, "Best supplier we work with in Harare — 10/10."),
]

BRANDS_DATA = [
    ("Chicken Inn",  "Sam Levy's Village", "Harare"),
    ("Chicken Inn",  "Bulawayo CBD",        "Bulawayo"),
    ("KFC Zimbabwe", "Westgate",            "Harare"),
    ("KFC Zimbabwe", "Borrowdale",          "Harare"),
    ("Galito's",     "Avondale",            "Harare"),
    ("Galito's",     "Newtown Mall",        "Bulawayo"),
    ("Pizza Inn",    "Joina City",          "Harare"),
    ("Steers",       "Eastgate Mall",       "Harare"),
    ("Nando's",      "Borrowdale Brooke",   "Harare"),
]

ZIM_NAMES = [
    ("Tatenda Moyo",          "Harare",   "18-24"),
    ("Rudo Chigwedere",       "Bulawayo", "25-34"),
    ("Farai Mutasa",          "Harare",   "35-44"),
    ("Simba Ndlovu",          "Mutare",   "18-24"),
    ("Chipo Dube",            "Harare",   "25-34"),
    ("Tawanda Ncube",         "Gweru",    "18-24"),
    ("Nyasha Mlambo",         "Harare",   "25-34"),
    ("Kudzai Zvenyika",       "Bulawayo", "35-44"),
    ("Grace Chirwa",          "Harare",   "18-24"),
    ("Admire Gumbo",          "Harare",   "25-34"),
    ("Blessing Sibanda",      "Mutare",   "18-24"),
    ("Munyaradzi Chiweshe",   "Harare",   "45-54"),
    ("Tendai Mhuri",          "Harare",   "25-34"),
    ("Prosper Mlambo",        "Bulawayo", "18-24"),
    ("Chenai Dziva",          "Harare",   "35-44"),
]

EXPERIENCES = [
    "The food was absolutely delicious and the service was very fast. Will definitely come back!",
    "The chicken was crispy and fresh. However, the waiting time was a bit long during lunch hour.",
    "Great ambience and clean environment. The staff were friendly and professional.",
    "Portion sizes have reduced compared to last year. Pricing feels a bit steep for the quantity.",
    "Had a wonderful experience at the Borrowdale branch. Food was hot and perfectly seasoned.",
    "The queue was too long and the air conditioning was not working. Food was average.",
    "Best fast food in Harare! The grilled chicken is outstanding and the chips are always fresh.",
    "The branch in Eastgate was clean and well-managed. I enjoyed every bite.",
]

RECOMMENDATIONS = [
    {
        "report_type": "risk",
        "title": "High Risk Supplier Alert — Delivery Reliability",
        "description": "Three suppliers have shown a pattern of late deliveries over the past 90 days, creating stock-out risk for peak trading periods.",
        "key_metrics": {"late_delivery_rate": 38.5, "avg_delay_days": 4.2, "affected_skus": 12},
        "insights": "Irvine's and Colcom have maintained strong reliability. Risk is concentrated in smaller distributors.",
        "recommended_actions": "Dual-source high-demand SKUs. Issue formal performance warning to affected suppliers. Review SLA terms.",
        "confidence_level": 0.84,
        "generated_by": "Risk Analysis Engine v2",
    },
    {
        "report_type": "performance",
        "title": "Top Performer Recognition — Q2 2025",
        "description": "Supplier performance analysis for Q2 2025 identifies top and bottom performers across timeliness, quality, and compliance.",
        "key_metrics": {"top_supplier": "Irvine's Zimbabwe", "avg_score": 78.4, "below_threshold": 2},
        "insights": "Irvine's Zimbabwe leads with a final performance score of 91.3. Two suppliers fall below the 60-point threshold.",
        "recommended_actions": "Reward top performers with preferred supplier status. Place underperformers on a 30-day improvement plan.",
        "confidence_level": 0.91,
        "generated_by": "Performance Module v3",
    },
    {
        "report_type": "inventory",
        "title": "Reorder Alert — Critical SKUs Below Threshold",
        "description": "5 inventory items are at or below their reorder level, with projected stock-out within 7 days at current consumption rates.",
        "key_metrics": {"items_below_reorder": 5, "projected_stockout_days": 7, "value_at_risk_usd": 1840},
        "insights": "Frozen Chicken Wings and Cooking Oil are the highest-risk items given current demand trends.",
        "recommended_actions": "Raise emergency purchase orders for critical SKUs. Negotiate expedited delivery with Irvine's and National Foods.",
        "confidence_level": 0.96,
        "generated_by": "Inventory Forecasting Engine",
    },
    {
        "report_type": "sentiment",
        "title": "Customer Sentiment Trend — Chicken Inn Harare Branches",
        "description": "Sentiment analysis of 320 reviews over the last 60 days shows a decline in positive sentiment for Harare CBD branches.",
        "key_metrics": {"positive_pct": 52, "neutral_pct": 28, "negative_pct": 20, "nps_avg": 6.2},
        "insights": "Waiting time and portion size are the primary drivers of negative sentiment. Staff friendliness remains highly rated.",
        "recommended_actions": "Review kitchen workflow during peak hours. Consider portion standardisation audit. Run staff appreciation programme.",
        "confidence_level": 0.79,
        "generated_by": "Sentiment Analysis Engine v2",
    },
]


class Command(BaseCommand):
    help = "Seed the database with realistic Zimbabwe data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing seeded data before reseeding",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write(self.style.WARNING("Flushing existing data..."))
            # Order matters — delete dependents first
            SentimentAnalysis.objects.all().delete()
            EngagementMetric.objects.all().delete()
            Review.objects.all().delete()
            CustomerProfile.objects.all().delete()
            FastFoodBrand.objects.all().delete()
            SupplierSentiment.objects.all().delete()
            SupplierPerformanceScore.objects.all().delete()
            Complaint.objects.all().delete()
            SupplierReview.objects.all().delete()
            Delivery.objects.all().delete()
            Order.objects.all().delete()
            InventoryItem.objects.all().delete()
            Benchmark.objects.all().delete()
            MarketIndicator.objects.all().delete()
            CompetitorMarketData.objects.all().delete()
            MarketTrend.objects.all().delete()
            DecisionRecommendation.objects.all().delete()
            Supplier.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("  ✓ All tables cleared"))

        # ── 1. Suppliers ─────────────────────────────────────────────────────
        self.stdout.write("Seeding suppliers...")
        suppliers = []
        for s in SUPPLIERS_DATA:
            obj, _ = Supplier.objects.get_or_create(
                supplier_code=s["supplier_code"],
                defaults={**s, "is_active": True},
            )
            suppliers.append(obj)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(suppliers)} suppliers"))

        # ── 2. Orders ────────────────────────────────────────────────────────
        self.stdout.write("Seeding orders...")
        orders = []
        for supplier in suppliers:
            for _ in range(random.randint(4, 8)):
                product = random.choice(PRODUCTS)
                qty = random.randint(50, 500)
                expected = rand_future_date(45) if random.random() > 0.4 else rand_date(60, 5)
                status = random.choice(["PENDING", "CONFIRMED", "DISPATCHED", "DELIVERED", "DELIVERED", "DELIVERED"])
                order = Order.objects.create(
                    supplier=supplier,
                    product_name=product[0],
                    product_category=product[1],
                    sku=product[2],
                    quantity_ordered=qty,
                    unit_cost=Decimal(str(product[3])),
                    expected_delivery_date=expected,
                    status=status,
                    notes=random.choice(["Urgent — low stock", "Standard reorder", "Promotional stock-up", ""]),
                )
                orders.append(order)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(orders)} orders"))

        # ── 3. Deliveries ────────────────────────────────────────────────────
        self.stdout.write("Seeding deliveries...")
        delivered_orders = [o for o in orders if o.status == "DELIVERED"]
        deliveries = []
        for order in delivered_orders:
            exp = order.expected_delivery_date
            days_diff = random.randint(-3, 7)
            actual = exp + timedelta(days=days_diff)
            d_status = "EARLY" if days_diff < 0 else ("ON_TIME" if days_diff == 0 else "LATE")
            qty_delivered = int(order.quantity_ordered * random.choice([1.0, 1.0, 1.0, 0.9, 0.95]))
            condition = random.choices(["GOOD", "GOOD", "GOOD", "PARTIAL", "DAMAGED"], weights=[6, 6, 6, 2, 1])[0]
            driver = random.choice(DRIVERS)
            delivery = Delivery.objects.create(
                supplier=order.supplier,
                order_number=order.order_number,
                invoice_number=f"INV-{order.order_number[4:]}",
                product_category=order.product_category,
                quantity_ordered=order.quantity_ordered,
                quantity_delivered=qty_delivered,
                expected_delivery_date=exp,
                actual_delivery_date=actual,
                delivery_status=d_status,
                condition_status=condition,
                driver_name=driver[0],
                vehicle_registration=driver[1],
                documentation_complete=random.choice([True, True, True, False]),
            )
            deliveries.append(delivery)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(deliveries)} deliveries"))

        # ── 4. Supplier Reviews ──────────────────────────────────────────────
        self.stdout.write("Seeding supplier reviews...")
        for supplier in suppliers:
            for _ in range(random.randint(2, 5)):
                SupplierReview.objects.create(
                    supplier=supplier,
                    communication_score=round(random.uniform(55, 98), 1),
                    flexibility_score=round(random.uniform(50, 95), 1),
                    price_competitiveness_score=round(random.uniform(60, 95), 1),
                    documentation_score=round(random.uniform(65, 100), 1),
                    review_comment=random.choice(REVIEW_COMMENTS),
                )
        self.stdout.write(self.style.SUCCESS("  ✓ supplier reviews done"))

        # ── 5. Complaints ────────────────────────────────────────────────────
        self.stdout.write("Seeding complaints...")
        for supplier in suppliers:
            for _ in range(random.randint(0, 3)):
                Complaint.objects.create(
                    supplier=supplier,
                    description=random.choice(COMPLAINT_DESCS),
                    resolved=random.choice([True, True, False]),
                    severity_level=random.randint(1, 5),
                )
        self.stdout.write(self.style.SUCCESS("  ✓ complaints done"))

        # ── 6. Performance Scores ────────────────────────────────────────────
        self.stdout.write("Seeding supplier performance scores...")
        for supplier in suppliers:
            score, _ = SupplierPerformanceScore.objects.get_or_create(supplier=supplier)
            score.timeliness_score        = round(random.uniform(50, 98), 2)
            score.quantity_accuracy_score = round(random.uniform(60, 99), 2)
            score.quality_score           = round(random.uniform(55, 98), 2)
            score.complaint_score         = round(random.uniform(40, 95), 2)
            score.consistency_score       = round(random.uniform(55, 97), 2)
            score.risk_index              = round(random.uniform(5, 40), 2)
            score.trust_index             = round(random.uniform(50, 95), 2)
            score.calculate_final_score()
        self.stdout.write(self.style.SUCCESS("  ✓ performance scores done"))

        # ── 7. Supplier Sentiments ───────────────────────────────────────────
        self.stdout.write("Seeding supplier sentiments...")
        for supplier in suppliers:
            for _ in range(random.randint(2, 4)):
                s = random.choice(SENTIMENTS)
                SupplierSentiment.objects.create(
                    supplier=supplier,
                    source_type=random.choice(["DELIVERY", "REVIEW", "COMPLAINT"]),
                    source_id=random.randint(1, 100),
                    text=s[2],
                    sentiment_label=s[0],
                    confidence_score=s[1],
                )
        self.stdout.write(self.style.SUCCESS("  ✓ sentiments done"))

        # ── 8. Fast Food Brands ──────────────────────────────────────────────
        self.stdout.write("Seeding fast food brands...")
        brands = []
        for b in BRANDS_DATA:
            obj, _ = FastFoodBrand.objects.get_or_create(name=b[0], branch=b[1], location=b[2])
            brands.append(obj)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(brands)} brands"))

        # ── 9. Customer Profiles ─────────────────────────────────────────────
        self.stdout.write("Seeding customer profiles...")
        profiles = []
        for name, location, age_range in ZIM_NAMES:
            p, _ = CustomerProfile.objects.get_or_create(
                full_name=name,
                defaults={
                    "age_range": age_range,
                    "gender": random.choice(["Male", "Female"]),
                    "location": location,
                    "employment_status": random.choice(["Employed", "Self-Employed", "Student", "Unemployed"]),
                    "eating_out_frequency": random.choice(["Daily", "2-3x per week", "Weekly", "Fortnightly"]),
                    "preferred_brand": random.choice(["Chicken Inn", "KFC Zimbabwe", "Galito's", "Pizza Inn", "Steers"]),
                },
            )
            profiles.append(p)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(profiles)} customer profiles"))

        # ── 10. Reviews ──────────────────────────────────────────────────────
        self.stdout.write("Seeding reviews...")
        reviews = []
        for _ in range(40):
            r = Review.objects.create(
                customer=random.choice(profiles),
                brand=random.choice(brands),
                taste=random.randint(2, 5), freshness=random.randint(2, 5),
                portion_size=random.randint(1, 5), presentation=random.randint(2, 5),
                menu_variety=random.randint(2, 5), food_value=random.randint(2, 5),
                staff_friendliness=random.randint(2, 5), professionalism=random.randint(2, 5),
                order_accuracy=random.randint(2, 5), waiting_time=random.randint(1, 5),
                problem_resolution=random.randint(2, 5), cleanliness=random.randint(2, 5),
                ambience=random.randint(2, 5), seating=random.randint(2, 5),
                hygiene=random.randint(2, 5), affordability=random.randint(1, 5),
                pricing_fairness=random.randint(1, 5), promotions=random.randint(1, 5),
                brand_reputation=random.randint(2, 5), food_trust=random.randint(2, 5),
                nps_score=random.randint(1, 10),
                vs_chickeninn=random.choice(["Better", "Same", "Worse", None]),
                vs_kfc=random.choice(["Better", "Same", "Worse", None]),
                vs_galitos=random.choice(["Better", "Same", "Worse", None]),
                full_experience=random.choice(EXPERIENCES),
                improvement_suggestions=random.choice([
                    "More parking space needed.", "Reduce waiting time during peak hours.",
                    "Add a loyalty rewards programme.", "More vegetarian options on the menu.", "",
                ]),
                overall_weighted_score=round(random.uniform(2.0, 5.0), 2),
                competitor_advantage=round(random.uniform(-20, 30), 2),
            )
            reviews.append(r)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(reviews)} reviews"))

        # ── 11. Sentiment Analysis ───────────────────────────────────────────
        self.stdout.write("Seeding sentiment analyses...")
        for review in reviews:
            vader = round(random.uniform(-1, 1), 4)
            bert  = round(random.uniform(0, 1), 4)
            final = round((vader + bert) / 2, 4)
            label = "Positive" if final > 0.3 else ("Negative" if final < -0.1 else "Neutral")
            SentimentAnalysis.objects.get_or_create(
                review=review,
                defaults={"vader_score": vader, "bert_score": bert, "final_sentiment_score": final, "sentiment_label": label},
            )
        self.stdout.write(self.style.SUCCESS("  ✓ sentiment analyses done"))

        # ── 12. Engagement Metrics ───────────────────────────────────────────
        self.stdout.write("Seeding engagement metrics...")
        for review in random.sample(reviews, min(20, len(reviews))):
            EngagementMetric.objects.create(
                customer=review.customer, review=review,
                page_views=random.randint(1, 30), clicks=random.randint(0, 15),
                messages_sent=random.randint(0, 5), support_tickets=random.randint(0, 2),
                engagement_score=round(random.uniform(20, 95), 2),
                loyalty_index=round(random.uniform(10, 90), 2),
            )
        self.stdout.write(self.style.SUCCESS("  ✓ engagement metrics done"))

        # ── 13. Inventory ────────────────────────────────────────────────────
        self.stdout.write("Seeding inventory...")
        used_skus = set(InventoryItem.objects.values_list("sku", flat=True))
        for supplier in suppliers[:5]:
            for product in random.sample(PRODUCTS, random.randint(3, 6)):
                if product[2] in used_skus:
                    continue
                used_skus.add(product[2])
                InventoryItem.objects.create(
                    sku=product[2],
                    supplier=supplier,
                    name=product[0],
                    category=product[1],
                    description=f"Standard {product[1].lower()} product supplied by {supplier.name}.",
                    quantity_in_stock=random.randint(50, 800),
                    reorder_level=random.randint(20, 100),
                    unit_cost=Decimal(str(product[3])),
                    selling_price=Decimal(str(round(product[3] * 1.35, 2))),
                    warehouse_location=random.choice([
                        "Warehouse A - Harare", "Warehouse B - Msasa",
                        "Cold Store 1", "Dry Store 2", "Bulawayo Hub"
                    ]),
                    last_restocked=timezone.now() - timedelta(days=random.randint(1, 30)),
                    is_active=True,
                )
        self.stdout.write(self.style.SUCCESS("  ✓ inventory done"))

        # ── 14. Market Trends ────────────────────────────────────────────────
        self.stdout.write("Seeding market trends...")
        trend_data = [
            {
                "industry": "Fast Food", "market_region": "Harare Metropolitan",
                "trend_title": "Zimbabwe Fast Food Market Growth 2024–2025",
                "trend_summary": "The Zimbabwean fast food sector continues to expand driven by urbanisation, a growing youth population, and increasing mobile payment penetration via EcoCash.",
                "overall_growth_rate": 8.4, "market_size_value": 420.5,
                "inflation_impact_index": 62.3, "consumer_spending_index": 55.8,
                "risk_level": 45.2, "political_risk_index": 55.0,
                "economic_volatility_index": 67.5, "supply_chain_stability_index": 48.3,
                "online_ordering_growth": 34.7, "delivery_adoption_rate": 22.1,
                "youth_demand_index": 78.4, "data_source": "Zimbabwe National Statistics Agency (ZIMSTAT)",
                "analysis_model": "BERT + Regression", "confidence_score": 0.81,
                "start_period": date(2024, 1, 1), "end_period": date(2025, 6, 30),
            },
            {
                "industry": "Quick Service Restaurant", "market_region": "Bulawayo & Matabeleland",
                "trend_title": "QSR Expansion in Bulawayo 2024",
                "trend_summary": "Bulawayo is seeing renewed investment in quick service restaurants as economic conditions stabilise.",
                "overall_growth_rate": 5.9, "market_size_value": 180.2,
                "inflation_impact_index": 58.1, "consumer_spending_index": 48.3,
                "risk_level": 38.7, "political_risk_index": 42.0,
                "economic_volatility_index": 55.0, "supply_chain_stability_index": 52.0,
                "online_ordering_growth": 18.5, "delivery_adoption_rate": 15.3,
                "youth_demand_index": 65.2, "data_source": "Bulawayo City Council Economic Report 2024",
                "analysis_model": "VADER + Logistic Regression", "confidence_score": 0.74,
                "start_period": date(2024, 1, 1), "end_period": date(2024, 12, 31),
            },
            {
                "industry": "Food Delivery", "market_region": "Zimbabwe National",
                "trend_title": "EcoCash-Driven Food Delivery Surge 2025",
                "trend_summary": "Mobile payment infrastructure via EcoCash has enabled rapid growth in food delivery, particularly among 18-34 urban consumers.",
                "overall_growth_rate": 21.3, "market_size_value": 95.8,
                "inflation_impact_index": 50.4, "consumer_spending_index": 62.7,
                "risk_level": 32.1, "political_risk_index": 38.0,
                "economic_volatility_index": 48.5, "supply_chain_stability_index": 60.2,
                "online_ordering_growth": 56.8, "delivery_adoption_rate": 41.3,
                "youth_demand_index": 84.6, "data_source": "Econet Wireless Zimbabwe Annual Report 2024",
                "analysis_model": "Transformer + Time Series", "confidence_score": 0.87,
                "start_period": date(2024, 6, 1), "end_period": date(2025, 5, 31),
            },
        ]
        trends = []
        for td in trend_data:
            t, _ = MarketTrend.objects.get_or_create(trend_title=td["trend_title"], defaults=td)
            trends.append(t)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {len(trends)} market trends"))

        # ── 15. Market Indicators ────────────────────────────────────────────
        self.stdout.write("Seeding market indicators...")
        indicator_names = [
            ("Consumer Price Index",   "Economic",  "%"),
            ("USD Exchange Rate ZWL",  "Currency",  "ZWL"),
            ("Chicken Wholesale Price","Commodity", "USD/kg"),
            ("Fuel Price Harare",      "Logistics", "USD/L"),
            ("Youth Unemployment Rate","Labour",    "%"),
        ]
        for trend in trends:
            for ind_name, ind_cat, unit in indicator_names:
                MarketIndicator.objects.create(
                    trend=trend, indicator_name=ind_name, indicator_category=ind_cat,
                    value=round(random.uniform(10, 350), 2), unit=unit,
                    recorded_date=rand_date(180, 30),
                )
        self.stdout.write(self.style.SUCCESS("  ✓ market indicators done"))

        # ── 16. Competitor Market Data ───────────────────────────────────────
        self.stdout.write("Seeding competitor market data...")
        competitors = [
            ("Chicken Inn",  28.4, 4.50, 32.5, 9.2,  74.3),
            ("KFC Zimbabwe", 22.1, 5.80, 26.8, 7.4,  78.1),
            ("Galito's",     12.6, 6.20, 14.2, 11.3, 72.5),
            ("Pizza Inn",    10.2, 5.50, 11.8, 5.6,  68.4),
            ("Steers",        8.7, 5.10,  9.4, 4.2,  65.8),
            ("Nando's",       6.3, 7.20,  7.1, 6.8,  76.2),
        ]
        for trend in trends:
            for comp in competitors:
                CompetitorMarketData.objects.create(
                    trend=trend, brand_name=comp[0],
                    market_share_percentage=comp[1] + random.uniform(-2, 2),
                    average_price=comp[2],
                    revenue_estimate=comp[3] * random.uniform(0.9, 1.1),
                    brand_growth_rate=comp[4],
                    customer_satisfaction_index=comp[5] + random.uniform(-5, 5),
                    social_media_mentions=random.randint(200, 5000),
                    search_trend_index=round(random.uniform(30, 95), 2),
                    recorded_date=rand_date(90, 7),
                )
        self.stdout.write(self.style.SUCCESS("  ✓ competitor data done"))

        # ── 17. Benchmarks ───────────────────────────────────────────────────
        self.stdout.write("Seeding benchmarks...")
        metrics = ["On-Time Delivery Rate", "Order Fill Rate", "Invoice Accuracy", "Lead Time (days)", "Return Rate %"]
        for supplier in suppliers:
            for metric in metrics:
                Benchmark.objects.create(
                    supplier=supplier, metric_name=metric,
                    metric_value=round(random.uniform(55, 98), 2),
                    industry_average=round(random.uniform(60, 85), 2),
                    percentile_rank=round(random.uniform(20, 95), 2),
                    benchmark_score=round(random.uniform(50, 100), 2),
                    evaluation_period="Q1-Q2 2025",
                    notes="Based on Zimbabwe food distribution industry averages.",
                )
        self.stdout.write(self.style.SUCCESS("  ✓ benchmarks done"))

        # ── 18. Decision Recommendations ────────────────────────────────────
        self.stdout.write("Seeding decision recommendations...")
        for rec in RECOMMENDATIONS:
            DecisionRecommendation.objects.get_or_create(title=rec["title"], defaults=rec)
        self.stdout.write(self.style.SUCCESS("  ✓ decision recommendations done"))

        # ── Summary ──────────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS("\n✅ All seed data loaded successfully!"))
        self.stdout.write(f"   Suppliers:  {Supplier.objects.count()}")
        self.stdout.write(f"   Orders:     {Order.objects.count()}")
        self.stdout.write(f"   Deliveries: {Delivery.objects.count()}")
        self.stdout.write(f"   Reviews:    {Review.objects.count()}")
        self.stdout.write(f"   Inventory:  {InventoryItem.objects.count()}")