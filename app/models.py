from django.conf import settings
from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models
from django.utils import timezone


from django.db import models
from django.utils import timezone

class VisitorLog(models.Model):
    """
    Captures basic visit metadata for auditing/analytics.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=512)
    method = models.CharField(max_length=10)
    user_agent = models.TextField(blank=True)
    referrer = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True, default="Unknown")
    visited_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-visited_at"]
        indexes = [
            models.Index(fields=["visited_at"]),
            models.Index(fields=["path"]),
            models.Index(fields=["ip_address"]),
        ]

    def __str__(self) -> str:
        ip = self.ip_address or "Unknown IP"
        return f"{self.path} @ {self.visited_at:%Y-%m-%d %H:%M:%S} ({ip})"





class Supplier(models.Model):
    supplier_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    tax_number = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company_name})"


from django.db import models
from django.utils import timezone


class Supplier(models.Model):
    supplier_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    tax_number = models.CharField(max_length=100, blank=True, null=True)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company_name})"



class SupplierPerformanceScore(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE)

    timeliness_score = models.FloatField(default=0)
    quantity_accuracy_score = models.FloatField(default=0)
    quality_score = models.FloatField(default=0)
    complaint_score = models.FloatField(default=0)
    consistency_score = models.FloatField(default=0)

    final_score = models.FloatField(default=0)
    rating_category = models.CharField(max_length=50, blank=True)

    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Performance - {self.supplier.name}"


class SupplierSentiment(models.Model):
    SOURCE_TYPE = (
        ('DELIVERY', 'Delivery Note'),
        ('REVIEW', 'Review Comment'),
        ('COMPLAINT', 'Complaint'),
    )

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="sentiments")

    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE)
    source_id = models.IntegerField()  # id of delivery/review/complaint

    text = models.TextField()

    sentiment_label = models.CharField(max_length=20)
    confidence_score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.sentiment_label}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    customer_code = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=100, blank=True)

    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    purchase_frequency = models.FloatField(default=0.0)
    churn_probability = models.FloatField(default=0.0)

    engagement_score = models.FloatField(default=0.0)
    trust_score = models.FloatField(default=0.0)

    registration_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username



# ---------------------------------------
# Customer Profile (anonymous-friendly)
# ---------------------------------------
class CustomerProfile(models.Model):
    full_name = models.CharField(max_length=100)
    age_range = models.CharField(max_length=50)
    gender = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100)
    employment_status = models.CharField(max_length=50, blank=True, null=True)
    eating_out_frequency = models.CharField(max_length=50, blank=True, null=True)
    preferred_brand = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.location}"


# ---------------------------------------
# Fast Food Brand / Restaurant
# ---------------------------------------
class FastFoodBrand(models.Model):
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


# ---------------------------------------
# Customer Review
# ---------------------------------------
class Review(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    brand = models.ForeignKey(FastFoodBrand, on_delete=models.CASCADE)

    # Food Quality
    taste = models.IntegerField()
    freshness = models.IntegerField()
    portion_size = models.IntegerField()
    presentation = models.IntegerField()
    menu_variety = models.IntegerField()
    food_value = models.IntegerField()

    # Service
    staff_friendliness = models.IntegerField()
    professionalism = models.IntegerField()
    order_accuracy = models.IntegerField()
    waiting_time = models.IntegerField()
    problem_resolution = models.IntegerField()

    # Environment
    cleanliness = models.IntegerField()
    ambience = models.IntegerField()
    seating = models.IntegerField()
    hygiene = models.IntegerField()

    # Pricing
    affordability = models.IntegerField()
    pricing_fairness = models.IntegerField()
    promotions = models.IntegerField()

    # Brand & Loyalty
    brand_reputation = models.IntegerField()
    food_trust = models.IntegerField()
    nps_score = models.IntegerField()

    # Competitor comparison (text fields)
    vs_chickeninn = models.CharField(max_length=20, blank=True, null=True)
    vs_kfc = models.CharField(max_length=20, blank=True, null=True)
    vs_galitos = models.CharField(max_length=20, blank=True, null=True)

    # Open text
    full_experience = models.TextField()
    improvement_suggestions = models.TextField(blank=True, null=True)

    # Calculated fields
    overall_weighted_score = models.FloatField(null=True, blank=True)
    competitor_advantage = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand.name} review by {self.customer.full_name}"


# ---------------------------------------
# Sentiment Analysis
# ---------------------------------------
class SentimentAnalysis(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE)

    vader_score = models.FloatField()
    bert_score = models.FloatField()
    final_sentiment_score = models.FloatField()
    sentiment_label = models.CharField(max_length=50)

    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sentiment for {self.review}"


# ---------------------------------------
# Customer Engagement Metrics
# ---------------------------------------
class EngagementMetric(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    page_views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    support_tickets = models.IntegerField(default=0)
    engagement_score = models.FloatField(default=0)
    loyalty_index = models.FloatField(default=0)

    recorded_month = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Engagement for {self.customer.full_name}"






class InventoryItem(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    quantity_in_stock = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField()

    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    warehouse_location = models.CharField(max_length=255)

    last_restocked = models.DateTimeField(null=True, blank=True)
    last_sold = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name



class DecisionRecommendation(models.Model):
    REPORT_TYPE = [
        ('risk', 'Risk Analysis'),
        ('performance', 'Performance'),
        ('inventory', 'Inventory'),
        ('sentiment', 'Sentiment'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPE)
    title = models.CharField(max_length=255)
    description = models.TextField()

    key_metrics = models.JSONField()
    insights = models.TextField()
    recommended_actions = models.TextField()

    confidence_level = models.FloatField()
    generated_by = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Benchmark(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()

    industry_average = models.FloatField()
    percentile_rank = models.FloatField()

    benchmark_score = models.FloatField()
    evaluation_period = models.CharField(max_length=50)

    notes = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.metric_name} - {self.supplier}"
class MarketTrend(models.Model):
    INDUSTRY_CHOICES = [
        ("Fast Food", "Fast Food"),
        ("Quick Service Restaurant", "Quick Service Restaurant"),
        ("Food Delivery", "Food Delivery"),
    ]

    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES)
    market_region = models.CharField(max_length=150)  # e.g. Zimbabwe, Harare

    trend_title = models.CharField(max_length=255)
    trend_summary = models.TextField()

    # Core Metrics
    overall_growth_rate = models.FloatField(help_text="Annual market growth %")
    market_size_value = models.FloatField(help_text="Total market size in USD")
    inflation_impact_index = models.FloatField(default=0)
    consumer_spending_index = models.FloatField(default=0)

    # Risk & Stability
    risk_level = models.FloatField(help_text="0–100 scale")
    political_risk_index = models.FloatField(default=0)
    economic_volatility_index = models.FloatField(default=0)
    supply_chain_stability_index = models.FloatField(default=0)

    # Digital & Consumer Shift
    online_ordering_growth = models.FloatField(default=0)
    delivery_adoption_rate = models.FloatField(default=0)
    youth_demand_index = models.FloatField(default=0)

    # Source & AI metadata
    data_source = models.CharField(max_length=255)
    source_url = models.URLField(blank=True, null=True)
    scraped_at = models.DateTimeField(null=True, blank=True)

    analysis_model = models.CharField(max_length=100)  # e.g. Prophet, ARIMA, Regression
    confidence_score = models.FloatField(default=0)

    start_period = models.DateField()
    end_period = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.trend_title
    
class MarketIndicator(models.Model):
    trend = models.ForeignKey(MarketTrend, on_delete=models.CASCADE, related_name="indicators")

    indicator_name = models.CharField(max_length=150)
    indicator_category = models.CharField(max_length=100)  # price, demand, revenue, share

    value = models.FloatField()
    unit = models.CharField(max_length=50)  # %, USD, Index

    recorded_date = models.DateField()

    def __str__(self):
        return f"{self.indicator_name} - {self.recorded_date}"



class ScrapedMarketSource(models.Model):
    source_name = models.CharField(max_length=255)
    source_url = models.URLField()

    raw_html = models.TextField()
    extracted_text = models.TextField()

    sentiment_score = models.FloatField(null=True, blank=True)

    scraped_at = models.DateTimeField(auto_now_add=True)

    processed = models.BooleanField(default=False)

    def __str__(self):
        return self.source_name


class CompetitorMarketData(models.Model):
    trend = models.ForeignKey(MarketTrend, on_delete=models.CASCADE, related_name="competitors")

    brand_name = models.CharField(max_length=100)

    market_share_percentage = models.FloatField()
    average_price = models.FloatField()
    revenue_estimate = models.FloatField()

    brand_growth_rate = models.FloatField()
    customer_satisfaction_index = models.FloatField()

    social_media_mentions = models.IntegerField(default=0)
    search_trend_index = models.FloatField(default=0)

    recorded_date = models.DateField()

    def __str__(self):
        return f"{self.brand_name} - {self.recorded_date}"



class SupplierPerformanceScore(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE)

    # Core performance metrics
    timeliness_score = models.FloatField(default=0)
    quantity_accuracy_score = models.FloatField(default=0)
    quality_score = models.FloatField(default=0)
    complaint_score = models.FloatField(default=0)
    consistency_score = models.FloatField(default=0)

    # Additional indices
    risk_index = models.FloatField(default=0, help_text="Higher = more risk")
    trust_index = models.FloatField(default=0, help_text="Higher = more trusted")

    # Final aggregated score
    final_score = models.FloatField(default=0)
    rating_category = models.CharField(max_length=50, blank=True)

    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Performance - {self.supplier.name}"

    def calculate_final_score(self, weights=None):
        """
        Compute weighted final score including risk and trust indices.
        weights: dict with optional weights for each metric
        """
        # Default weights if none provided
        if weights is None:
            weights = {
                "timeliness": 0.2,
                "quantity_accuracy": 0.2,
                "quality": 0.2,
                "complaint": 0.15,
                "consistency": 0.1,
                "trust_index": 0.1,
                "risk_index": -0.05  # negative weight because high risk reduces score
            }

        score = (
            self.timeliness_score * weights["timeliness"] +
            self.quantity_accuracy_score * weights["quantity_accuracy"] +
            self.quality_score * weights["quality"] +
            self.complaint_score * weights["complaint"] +
            self.consistency_score * weights["consistency"] +
            self.trust_index * weights["trust_index"] +
            self.risk_index * weights["risk_index"]
        )

        self.final_score = max(min(score, 100), 0)  # Cap between 0–100
        self.rating_category = self.get_rating_category()
        self.last_updated = timezone.now()
        self.save()
        return self.final_score

    def get_rating_category(self):
        """Assign category based on final score"""
        if self.final_score >= 85:
            return "Excellent"
        elif self.final_score >= 70:
            return "Good"
        elif self.final_score >= 50:
            return "Average"
        else:
            return "Poor"


class Delivery(models.Model):
    DELIVERY_STATUS = (
        ('ON_TIME', 'On Time'),
        ('LATE', 'Late'),
        ('EARLY', 'Early'),
    )

    CONDITION_STATUS = (
        ('GOOD', 'Good'),
        ('DAMAGED', 'Damaged'),
        ('PARTIAL', 'Partial'),
    )

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="deliveries")

    order_number = models.CharField(max_length=100)
    invoice_number = models.CharField(max_length=100)

    product_category = models.CharField(max_length=255)
    quantity_ordered = models.IntegerField()
    quantity_delivered = models.IntegerField()

    expected_delivery_date = models.DateField()
    actual_delivery_date = models.DateField()

    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS)
    condition_status = models.CharField(max_length=20, choices=CONDITION_STATUS)

    documentation_complete = models.BooleanField(default=True)

    vehicle_registration = models.CharField(max_length=20, blank=True, null=True)
    driver_name = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier.name} - {self.order_number}"

class SupplierReview(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="reviews")

    communication_score = models.FloatField(default=0)
    flexibility_score = models.FloatField(default=0)
    price_competitiveness_score = models.FloatField(default=0)
    documentation_score = models.FloatField(default=0)

    review_comment = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review - {self.supplier.name}"


class Complaint(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="complaints")

    description = models.TextField()
    resolved = models.BooleanField(default=False)
    severity_level = models.IntegerField(default=1)  # 1–5 scale

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint - {self.supplier.name}"
