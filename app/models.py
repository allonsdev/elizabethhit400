from django.conf import settings
from django.db import models
from django.utils import timezone


# ---------------------------------------
# Visitor Logs
# ---------------------------------------
class VisitorLog(models.Model):
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
        verbose_name = "Visitor Log"
        verbose_name_plural = "Visitor Logs"
        ordering = ["-visited_at"]
        indexes = [
            models.Index(fields=["visited_at"]),
            models.Index(fields=["path"]),
            models.Index(fields=["ip_address"]),
        ]

    def __str__(self):
        return f"{self.path} @ {self.visited_at}"


# ---------------------------------------
# Supplier
# ---------------------------------------
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

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return f"{self.name} ({self.company_name})"


# ---------------------------------------
# Supplier Performance Score
# ---------------------------------------
class SupplierPerformanceScore(models.Model):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE)

    timeliness_score = models.FloatField(default=0)
    quantity_accuracy_score = models.FloatField(default=0)
    quality_score = models.FloatField(default=0)
    complaint_score = models.FloatField(default=0)
    consistency_score = models.FloatField(default=0)
    risk_index = models.FloatField(default=0)
    trust_index = models.FloatField(default=0)

    final_score = models.FloatField(default=0)
    rating_category = models.CharField(max_length=50, blank=True)
    last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Supplier Performance Score"
        verbose_name_plural = "Supplier Performance Scores"

    def __str__(self):
        return f"Performance - {self.supplier.name}"

    def calculate_final_score(self, weights=None):
        if weights is None:
            weights = {
                "timeliness": 0.2,
                "quantity_accuracy": 0.2,
                "quality": 0.2,
                "complaint": 0.15,
                "consistency": 0.1,
                "trust_index": 0.1,
                "risk_index": -0.05,
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

        self.final_score = max(min(score, 100), 0)
        self.rating_category = self.get_rating_category()
        self.last_updated = timezone.now()
        self.save()
        return self.final_score

    def get_rating_category(self):
        if self.final_score >= 85:
            return "Excellent"
        elif self.final_score >= 70:
            return "Good"
        elif self.final_score >= 50:
            return "Average"
        return "Poor"
    
    
    # def update_from_review(self, review):
    #     """
    #     Update the performance scores based on a review object.
    #     Example mapping: you can adjust based on your fields.
    #     """
    #     self.timeliness_score = review.timeliness or self.timeliness_score
    #     self.quality_score = review.quality or self.quality_score
    #     self.complaint_score = review.complaint_handling or self.complaint_score
    #     self.consistency_score = review.consistency or self.consistency_score
    #     self.quantity_accuracy_score = review.quantity_accuracy or self.quantity_accuracy_score

    #     # Recalculate final score
    #     self.calculate_final_score()

    # # -------------------------
    # # Update from sentiment analysis
    # # -------------------------
    # def update_from_sentiments(self):
    #     """
    #     Adjust trust_index or risk_index based on sentiment trends.
    #     This is just an example. You can make it more sophisticated.
    #     """
    #     # Example: positive sentiment increases trust_index
    #     reviews = self.supplier.review_set.all()
    #     total_reviews = reviews.count()
    #     if total_reviews == 0:
    #         return

    #     positive_reviews = reviews.filter(sentimentanalysis__sentiment_label="Positive").count()
    #     self.trust_index = (positive_reviews / total_reviews) * 100

    #     # Negative reviews increase risk
    #     negative_reviews = reviews.filter(sentimentanalysis__sentiment_label="Negative").count()
    #     self.risk_index = (negative_reviews / total_reviews) * 100 * -1  # negative weight

    #     # Recalculate final score
    #     self.calculate_final_score()

# ---------------------------------------
# Supplier Sentiment
# ---------------------------------------
class SupplierSentiment(models.Model):
    SOURCE_TYPE = (
        ('DELIVERY', 'Delivery Note'),
        ('REVIEW', 'Review Comment'),
        ('COMPLAINT', 'Complaint'),
    )

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="sentiments"
    )
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE)
    source_id = models.IntegerField()
    text = models.TextField()
    sentiment_label = models.CharField(max_length=20)
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Supplier Sentiment"
        verbose_name_plural = "Supplier Sentiments"

    def __str__(self):
        return f"{self.supplier.name} - {self.sentiment_label}"


# ---------------------------------------
# Customer
# ---------------------------------------
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

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

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.user.username


# ---------------------------------------
# Customer Profile
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

    class Meta:
        verbose_name = "Customer Profile"
        verbose_name_plural = "Customer Profiles"

    def __str__(self):
        return f"{self.full_name} - {self.location}"


# ---------------------------------------
# Fast Food Brand
# ---------------------------------------
class FastFoodBrand(models.Model):
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Fast Food Brand"
        verbose_name_plural = "Fast Food Brands"

    def __str__(self):
        return self.name


# ---------------------------------------
# Review
# ---------------------------------------
class Review(models.Model):
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE)
    brand = models.ForeignKey(FastFoodBrand, on_delete=models.CASCADE)

    taste = models.IntegerField()
    freshness = models.IntegerField()
    portion_size = models.IntegerField()
    presentation = models.IntegerField()
    menu_variety = models.IntegerField()
    food_value = models.IntegerField()

    staff_friendliness = models.IntegerField()
    professionalism = models.IntegerField()
    order_accuracy = models.IntegerField()
    waiting_time = models.IntegerField()
    problem_resolution = models.IntegerField()

    cleanliness = models.IntegerField()
    ambience = models.IntegerField()
    seating = models.IntegerField()
    hygiene = models.IntegerField()

    affordability = models.IntegerField()
    pricing_fairness = models.IntegerField()
    promotions = models.IntegerField()

    brand_reputation = models.IntegerField()
    food_trust = models.IntegerField()
    nps_score = models.IntegerField()

    vs_chickeninn = models.CharField(max_length=20, blank=True, null=True)
    vs_kfc = models.CharField(max_length=20, blank=True, null=True)
    vs_galitos = models.CharField(max_length=20, blank=True, null=True)

    full_experience = models.TextField()
    improvement_suggestions = models.TextField(blank=True, null=True)

    overall_weighted_score = models.FloatField(null=True, blank=True)
    competitor_advantage = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

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

    class Meta:
        verbose_name = "Customer Sentiment Analysis"
        verbose_name_plural = "Customer Sentiment Analyses"

    def __str__(self):
        return f"Sentiment for {self.review}"


# ---------------------------------------
# Engagement Metrics
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

    class Meta:
        verbose_name = "Engagement Metric"
        verbose_name_plural = "Engagement Metrics"

    def __str__(self):
        return f"Engagement for {self.customer.full_name}"


# ---------------------------------------
# Inventory
# ---------------------------------------
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

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    def __str__(self):
        return self.name


# ---------------------------------------
# Decision Recommendation
# ---------------------------------------
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

    class Meta:
        verbose_name = "Decision Recommendation"
        verbose_name_plural = "Decision Recommendations"

    def __str__(self):
        return self.title


# ---------------------------------------
# Benchmark
# ---------------------------------------
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

    class Meta:
        verbose_name = "Benchmark"
        verbose_name_plural = "Benchmarks"

    def __str__(self):
        return f"{self.metric_name} - {self.supplier}"


# ---------------------------------------
# Market Trend
# ---------------------------------------
class MarketTrend(models.Model):
    INDUSTRY_CHOICES = [
        ("Fast Food", "Fast Food"),
        ("Quick Service Restaurant", "Quick Service Restaurant"),
        ("Food Delivery", "Food Delivery"),
    ]

    industry = models.CharField(max_length=100, choices=INDUSTRY_CHOICES)
    market_region = models.CharField(max_length=150)
    trend_title = models.CharField(max_length=255)
    trend_summary = models.TextField()

    overall_growth_rate = models.FloatField()
    market_size_value = models.FloatField()
    inflation_impact_index = models.FloatField(default=0)
    consumer_spending_index = models.FloatField(default=0)

    risk_level = models.FloatField()
    political_risk_index = models.FloatField(default=0)
    economic_volatility_index = models.FloatField(default=0)
    supply_chain_stability_index = models.FloatField(default=0)

    online_ordering_growth = models.FloatField(default=0)
    delivery_adoption_rate = models.FloatField(default=0)
    youth_demand_index = models.FloatField(default=0)

    data_source = models.CharField(max_length=255)
    source_url = models.URLField(blank=True, null=True)
    scraped_at = models.DateTimeField(null=True, blank=True)

    analysis_model = models.CharField(max_length=100)
    confidence_score = models.FloatField(default=0)

    start_period = models.DateField()
    end_period = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Market Trend"
        verbose_name_plural = "Market Trends"

    def __str__(self):
        return self.trend_title


# ---------------------------------------
# Market Indicator
# ---------------------------------------
class MarketIndicator(models.Model):
    trend = models.ForeignKey(
        MarketTrend, on_delete=models.CASCADE, related_name="indicators"
    )

    indicator_name = models.CharField(max_length=150)
    indicator_category = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    recorded_date = models.DateField()

    class Meta:
        verbose_name = "Market Indicator"
        verbose_name_plural = "Market Indicators"

    def __str__(self):
        return f"{self.indicator_name} - {self.recorded_date}"


# ---------------------------------------
# Scraped Market Source
# ---------------------------------------
class ScrapedMarketSource(models.Model):
    source_name = models.CharField(max_length=255)
    source_url = models.URLField()
    raw_html = models.TextField()
    extracted_text = models.TextField()
    sentiment_score = models.FloatField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Scraped Market Source"
        verbose_name_plural = "Scraped Market Sources"

    def __str__(self):
        return self.source_name


# ---------------------------------------
# Competitor Market Data
# ---------------------------------------
class CompetitorMarketData(models.Model):
    trend = models.ForeignKey(
        MarketTrend, on_delete=models.CASCADE, related_name="competitors"
    )

    brand_name = models.CharField(max_length=100)
    market_share_percentage = models.FloatField()
    average_price = models.FloatField()
    revenue_estimate = models.FloatField()
    brand_growth_rate = models.FloatField()
    customer_satisfaction_index = models.FloatField()
    social_media_mentions = models.IntegerField(default=0)
    search_trend_index = models.FloatField(default=0)
    recorded_date = models.DateField()

    class Meta:
        verbose_name = "Competitor Market Data"
        verbose_name_plural = "Competitor Market Data"

    def __str__(self):
        return f"{self.brand_name} - {self.recorded_date}"


# ---------------------------------------
# Delivery
# ---------------------------------------
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

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="deliveries"
    )

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

    class Meta:
        verbose_name = "Delivery"
        verbose_name_plural = "Deliveries"

    def __str__(self):
        return f"{self.supplier.name} - {self.order_number}"


# ---------------------------------------
# Supplier Review
# ---------------------------------------
class SupplierReview(models.Model):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="reviews"
    )

    communication_score = models.FloatField(default=0)
    flexibility_score = models.FloatField(default=0)
    price_competitiveness_score = models.FloatField(default=0)
    documentation_score = models.FloatField(default=0)
    review_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Supplier Review"
        verbose_name_plural = "Supplier Reviews"

    def __str__(self):
        return f"Review - {self.supplier.name}"


# ---------------------------------------
# Complaint
# ---------------------------------------
class Complaint(models.Model):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="complaints"
    )

    description = models.TextField()
    resolved = models.BooleanField(default=False)
    severity_level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Complaint"
        verbose_name_plural = "Complaints"

    def __str__(self):
        return f"Complaint - {self.supplier.name}"