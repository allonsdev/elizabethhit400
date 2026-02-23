from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from app.models import MarketTrend, MarketIndicator, CompetitorMarketData

fake = Faker()

class Command(BaseCommand):
    help = "Generate artificial market trend data"

    def handle(self, *args, **kwargs):

        brands = ["Nandos", "KFC", "Chicken Inn", "Galitos"]
        regions = ["Harare", "Bulawayo", "Zimbabwe"]

        for i in range(100):

            trend = MarketTrend.objects.create(
                industry="Fast Food",
                market_region=random.choice(regions),
                trend_title=fake.catch_phrase(),
                trend_summary=fake.text(max_nb_chars=300),
                overall_growth_rate=random.uniform(2, 15),
                market_size_value=random.uniform(10_000_000, 200_000_000),
                inflation_impact_index=random.uniform(0, 100),
                consumer_spending_index=random.uniform(0, 100),
                risk_level=random.uniform(0, 100),
                political_risk_index=random.uniform(0, 100),
                economic_volatility_index=random.uniform(0, 100),
                supply_chain_stability_index=random.uniform(0, 100),
                online_ordering_growth=random.uniform(5, 40),
                delivery_adoption_rate=random.uniform(10, 70),
                youth_demand_index=random.uniform(0, 100),
                data_source="Simulated Data Engine",
                source_url="https://simulated-data.com",
                scraped_at=timezone.now(),
                analysis_model=random.choice(["ARIMA", "Prophet", "Regression"]),
                confidence_score=random.uniform(60, 95),
                start_period=timezone.now().date(),
                end_period=timezone.now().date(),
            )

            # Add Indicators
            for month in range(1, 13):
                MarketIndicator.objects.create(
                    trend=trend,
                    indicator_name="Market Revenue",
                    indicator_category="Revenue",
                    value=random.uniform(500000, 5000000),
                    unit="USD",
                    recorded_date=timezone.now().date()
                )

            # Add Competitor Data
            for brand in brands:
                CompetitorMarketData.objects.create(
                    trend=trend,
                    brand_name=brand,
                    market_share_percentage=random.uniform(10, 40),
                    average_price=random.uniform(5, 15),
                    revenue_estimate=random.uniform(1_000_000, 10_000_000),
                    brand_growth_rate=random.uniform(1, 20),
                    customer_satisfaction_index=random.uniform(60, 95),
                    social_media_mentions=random.randint(1000, 50000),
                    search_trend_index=random.uniform(20, 100),
                    recorded_date=timezone.now().date()
                )

        self.stdout.write(self.style.SUCCESS("100 Market Trends Generated Successfully"))
