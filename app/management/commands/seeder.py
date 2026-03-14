from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone

from app.models import *

fake = Faker()


class Command(BaseCommand):

    help = "Seed Zimbabwe Fast Food Industry Data"

    def handle(self, *args, **kwargs):

        self.stdout.write("Deleting old data...")

        models = [
            SupplierPerformanceScore,
            SupplierSentiment,
            Delivery,
            InventoryItem,
            Complaint,
            SupplierReview,
            Benchmark,
            SentimentAnalysis,
            EngagementMetric,
            Review,
            FastFoodBrand,
            MarketIndicator,
            CompetitorMarketData,
            MarketTrend,
            ScrapedMarketSource,
            DecisionRecommendation,
            Supplier,
        ]

        for m in models:
            m.objects.all().delete()

        self.stdout.write("Old data cleared.")

        # -------------------------------------------------
        # SUPPLIERS
        # -------------------------------------------------

        suppliers = []

        zim_cities = [
            "Harare",
            "Bulawayo",
            "Mutare",
            "Gweru",
            "Masvingo",
            "Chitungwiza",
            "Kadoma",
        ]

        supplier_types = [
            "Poultry Suppliers",
            "Packaging Suppliers",
            "Frozen Food Suppliers",
            "Spice Suppliers",
            "Beverage Distributors",
        ]

        for i in range(120):

            s = Supplier.objects.create(
                supplier_code=f"S{i+1000}",
                name=f"{fake.company()} {random.choice(['Foods','Supplies','Distribution'])}",
                company_name=fake.company(),
                contact_person=fake.name(),
                email=fake.email(),
                phone=f"+2637{random.randint(10000000,99999999)}",
                location=random.choice(zim_cities),
                is_active=random.choice([True, True, True, False])
            )

            suppliers.append(s)

        # -------------------------------------------------
        # SUPPLIER PERFORMANCE
        # -------------------------------------------------

        scores = []

        for s in suppliers:

            score = SupplierPerformanceScore.objects.create(
                supplier=s,
                timeliness_score=random.uniform(60,95),
                quantity_accuracy_score=random.uniform(60,95),
                quality_score=random.uniform(60,95),
                complaint_score=random.uniform(50,90),
                consistency_score=random.uniform(60,95),
                risk_index=random.uniform(0,25),
                trust_index=random.uniform(60,95),
            )

            score.calculate_final_score()
            scores.append(score)

        # -------------------------------------------------
        # INVENTORY ITEMS
        # -------------------------------------------------

        inventory = []

        inventory_names = [
            "Chicken Pieces",
            "Burger Buns",
            "Frozen Chips",
            "Cooking Oil",
            "Soft Drink Syrup",
            "Packaging Boxes",
            "Chicken Spice Mix",
            "Grill Sauce",
        ]

        for i in range(200):

            item = InventoryItem.objects.create(
                supplier=random.choice(suppliers),
                sku=f"SKU{i+10000}",
                name=random.choice(inventory_names),
                category=random.choice(["Meat","Frozen","Packaging","Beverage","Spices"]),
                description=fake.text(),
                quantity_in_stock=random.randint(0,300),
                reorder_level=random.randint(10,50),
                unit_cost=random.uniform(1,20),
                selling_price=random.uniform(5,50),
                warehouse_location=random.choice(zim_cities),
            )

            inventory.append(item)

        # -------------------------------------------------
        # DELIVERIES
        # -------------------------------------------------

        deliveries = []

        for i in range(350):

            expected = fake.date_between("-90d","-5d")
            actual = expected + timedelta(days=random.randint(-2,4))

            d = Delivery.objects.create(
                supplier=random.choice(suppliers),
                order_number=f"ORD{i+2000}",
                invoice_number=f"INV{i+3000}",
                product_category=random.choice(["Chicken","Packaging","Beverages","Spices"]),
                quantity_ordered=random.randint(100,1000),
                quantity_delivered=random.randint(80,1000),
                expected_delivery_date=expected,
                actual_delivery_date=actual,
                delivery_status=random.choice(["ON_TIME","LATE","EARLY"]),
                condition_status=random.choice(["GOOD","DAMAGED","PARTIAL"]),
                documentation_complete=random.choice([True,True,True,False])
            )

            deliveries.append(d)

        # -------------------------------------------------
        # COMPLAINTS
        # -------------------------------------------------

        complaints = []

        for i in range(150):

            c = Complaint.objects.create(
                supplier=random.choice(suppliers),
                description=random.choice([
                    "Late delivery affecting lunch rush",
                    "Damaged chicken packaging",
                    "Missing items in shipment",
                    "Poor product quality",
                ]),
                resolved=random.choice([True, False]),
                severity_level=random.randint(1,5)
            )

            complaints.append(c)

        # -------------------------------------------------
        # SUPPLIER REVIEWS
        # -------------------------------------------------

        reviews = []

        for i in range(200):

            r = SupplierReview.objects.create(
                supplier=random.choice(suppliers),
                communication_score=random.uniform(60,95),
                flexibility_score=random.uniform(60,95),
                price_competitiveness_score=random.uniform(60,95),
                documentation_score=random.uniform(60,95),
                review_comment=fake.text()
            )

            reviews.append(r)

        # -------------------------------------------------
        # SUPPLIER SENTIMENTS
        # -------------------------------------------------

        sentiments = []

        for i in range(300):

            sentiment = SupplierSentiment.objects.create(
                supplier=random.choice(suppliers),
                source_type=random.choice(["DELIVERY","REVIEW","COMPLAINT"]),
                source_id=random.randint(1,500),
                text=fake.sentence(),
                sentiment_label=random.choice(["Positive","Neutral","Negative"]),
                confidence_score=random.uniform(0.6,0.95)
            )

            sentiments.append(sentiment)

        # -------------------------------------------------
        # FAST FOOD BRANDS
        # -------------------------------------------------

        brand_names = [
            "Chicken Inn",
            "Pizza Inn",
            "Creamy Inn",
            "Chicken Slice",
            "KFC Zimbabwe",
            "Galitos",
            "Nandos",
            "Steers",
        ]

        brands = []

        for i in range(20):

            brand = FastFoodBrand.objects.create(
                name=random.choice(brand_names),
                branch=fake.street_name(),
                location=random.choice(zim_cities)
            )

            brands.append(brand)

        # -------------------------------------------------
        # CUSTOMER REVIEWS
        # -------------------------------------------------

        review_objs = []

        profiles = list(CustomerProfile.objects.all())

        for i in range(300):

            if not profiles:
                break

            rev = Review.objects.create(
                customer=random.choice(profiles),
                brand=random.choice(brands),
                taste=random.randint(1,10),
                freshness=random.randint(1,10),
                portion_size=random.randint(1,10),
                presentation=random.randint(1,10),
                menu_variety=random.randint(1,10),
                food_value=random.randint(1,10),
                staff_friendliness=random.randint(1,10),
                professionalism=random.randint(1,10),
                order_accuracy=random.randint(1,10),
                waiting_time=random.randint(1,10),
                problem_resolution=random.randint(1,10),
                cleanliness=random.randint(1,10),
                ambience=random.randint(1,10),
                seating=random.randint(1,10),
                hygiene=random.randint(1,10),
                affordability=random.randint(1,10),
                pricing_fairness=random.randint(1,10),
                promotions=random.randint(1,10),
                brand_reputation=random.randint(1,10),
                food_trust=random.randint(1,10),
                nps_score=random.randint(1,10),
                full_experience=fake.text()
            )

            review_objs.append(rev)

        # -------------------------------------------------
        # SENTIMENT ANALYSIS
        # -------------------------------------------------

        for r in review_objs:

            SentimentAnalysis.objects.create(
                review=r,
                vader_score=random.uniform(-1,1),
                bert_score=random.uniform(-1,1),
                final_sentiment_score=random.uniform(-1,1),
                sentiment_label=random.choice(["Positive","Neutral","Negative"])
            )

        # -------------------------------------------------
        # ENGAGEMENT METRICS
        # -------------------------------------------------

        for r in review_objs:

            EngagementMetric.objects.create(
                customer=r.customer,
                review=r,
                page_views=random.randint(1,100),
                clicks=random.randint(1,50),
                messages_sent=random.randint(0,10),
                support_tickets=random.randint(0,5),
                engagement_score=random.uniform(0,100),
                loyalty_index=random.uniform(0,100)
            )

        # -------------------------------------------------
        # MARKET TRENDS
        # -------------------------------------------------

        trends = []

        for i in range(20):

            trend = MarketTrend.objects.create(
                industry="Fast Food",
                market_region="Zimbabwe",
                trend_title=fake.catch_phrase(),
                trend_summary=fake.text(),
                overall_growth_rate=random.uniform(2,15),
                market_size_value=random.uniform(1000000,8000000),
                risk_level=random.uniform(1,5),
                data_source="Zimbabwe Retail Association",
                analysis_model="AI Trend Model",
                confidence_score=random.uniform(70,95),
                start_period="2022-01-01",
                end_period="2026-01-01"
            )

            trends.append(trend)

        # -------------------------------------------------
        # MARKET INDICATORS
        # -------------------------------------------------

        for i in range(120):

            MarketIndicator.objects.create(
                trend=random.choice(trends),
                indicator_name="Fast Food Sales Index",
                indicator_category="Sales",
                value=random.uniform(50,150),
                unit="index",
                recorded_date=fake.date_this_year()
            )

        # -------------------------------------------------
        # COMPETITOR DATA
        # -------------------------------------------------

        for i in range(120):

            CompetitorMarketData.objects.create(
                trend=random.choice(trends),
                brand_name=random.choice(brand_names),
                market_share_percentage=random.uniform(5,30),
                average_price=random.uniform(3,12),
                revenue_estimate=random.uniform(50000,500000),
                brand_growth_rate=random.uniform(-5,15),
                customer_satisfaction_index=random.uniform(50,95),
                social_media_mentions=random.randint(100,5000),
                search_trend_index=random.uniform(30,100),
                recorded_date=fake.date_this_year()
            )

        # -------------------------------------------------
        # SCRAPED SOURCES
        # -------------------------------------------------

        for i in range(100):

            ScrapedMarketSource.objects.create(
                source_name=fake.company(),
                source_url=fake.url(),
                raw_html="<html></html>",
                extracted_text=fake.text(),
                sentiment_score=random.uniform(-1,1),
                processed=random.choice([True,False])
            )

        # -------------------------------------------------
        # AI DECISION REPORTS
        # -------------------------------------------------

        for i in range(100):

            DecisionRecommendation.objects.create(
                report_type=random.choice(["risk","performance","inventory","sentiment"]),
                title=fake.sentence(),
                description=fake.text(),
                key_metrics={"score": random.uniform(0,100)},
                insights=fake.text(),
                recommended_actions="Diversify suppliers and monitor delivery reliability.",
                confidence_level=random.uniform(70,95),
                generated_by="AI Supply Chain Model"
            )

        self.stdout.write(self.style.SUCCESS("Zimbabwe fast food dataset seeded successfully"))