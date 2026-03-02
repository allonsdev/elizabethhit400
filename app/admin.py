from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from .models import *


# ============================================================
# MARKET INDICATOR INLINE
# ============================================================
class MarketIndicatorInline(admin.TabularInline):
    model = MarketIndicator
    extra = 0
    show_change_link = True
    readonly_fields = ('status', 'color_indicator', 'rendered_data')

    def status(self, obj):
        return "High" if obj.value > 50 else "Low"

    def color_indicator(self, obj):
        return format_html(
            '<span style="color:{};">●</span>',
            'red' if obj.value > 50 else 'green'
        )

    def rendered_data(self, obj):
        return f"{obj.value} {obj.unit}"

    status.short_description = "Status"
    color_indicator.short_description = "Indicator"
    rendered_data.short_description = "Rendered Data"


# ============================================================
# COMPETITOR MARKET DATA INLINE
# ============================================================
class CompetitorMarketDataInline(admin.TabularInline):
    model = CompetitorMarketData
    extra = 0
    show_change_link = True
    readonly_fields = (
        'status',
        'color_indicator',
        'market_share_gap',
        'rendered_data',
    )

    def status(self, obj):
        return "Leader" if obj.market_share_percentage >= 50 else "Follower"

    def color_indicator(self, obj):
        return format_html(
            '<span style="color:{};">●</span>',
            'green' if obj.market_share_percentage >= 50 else 'orange'
        )

    def market_share_gap(self, obj):
        top = CompetitorMarketData.objects.filter(trend=obj.trend).aggregate(
            models.Max('market_share_percentage')
        )['market_share_percentage__max'] or 0
        return round(top - obj.market_share_percentage, 2)

    def rendered_data(self, obj):
        return f"{obj.market_share_percentage}% market share"

    status.short_description = "Status"
    color_indicator.short_description = "Indicator"
    market_share_gap.short_description = "Gap to Leader"
    rendered_data.short_description = "Rendered Data"


# ============================================================
# MARKET TREND ADMIN (AGGREGATED)
# ============================================================
@admin.register(MarketTrend)
class MarketTrendAdmin(admin.ModelAdmin):
    list_display = (
        "trend_title",
        "industry",
        "market_region",
        "overall_growth_rate",
        "market_size_value",
        "risk_level",
        "confidence_score",
        "indicator_count",
        "competitor_count",
    )

    list_filter = (
        "industry",
        "market_region",
        "analysis_model",
        "start_period",
        "end_period",
        "created_at",
    )

    search_fields = (
        "trend_title",
        "trend_summary",
        "market_region",
        "data_source",
    )

    date_hierarchy = "start_period"
    ordering = ("-start_period",)
    inlines = [MarketIndicatorInline, CompetitorMarketDataInline]

    readonly_fields = (
        "indicator_count",
        "competitor_count",
        "average_indicator_value",
    )

    fieldsets = (
        ("Basic Information", {
            "fields": ("industry", "market_region", "trend_title", "trend_summary")
        }),
        ("Analytics (Read Only)", {
            "fields": (
                "indicator_count",
                "competitor_count",
                "average_indicator_value",
            )
        }),
        ("Core Market Metrics", {
            "fields": (
                "overall_growth_rate",
                "market_size_value",
                "inflation_impact_index",
                "consumer_spending_index",
            )
        }),
        ("Risk & Stability", {
            "fields": (
                "risk_level",
                "political_risk_index",
                "economic_volatility_index",
                "supply_chain_stability_index",
            )
        }),
        ("Digital & Consumer Trends", {
            "fields": (
                "online_ordering_growth",
                "delivery_adoption_rate",
                "youth_demand_index",
            )
        }),
        ("Data Source & AI Analysis", {
            "fields": (
                "data_source",
                "source_url",
                "analysis_model",
                "confidence_score",
                "scraped_at",
            )
        }),
        ("Period", {
            "fields": ("start_period", "end_period")
        }),
    )

    def indicator_count(self, obj):
        return obj.indicators.count()

    def competitor_count(self, obj):
        return obj.competitors.count()

    def average_indicator_value(self, obj):
        return obj.indicators.aggregate(models.Avg('value'))['value__avg'] or 0

    indicator_count.short_description = "Indicators"
    competitor_count.short_description = "Competitors"
    average_indicator_value.short_description = "Avg Indicator"


# ============================================================
# VISITOR LOG ADMIN
# ============================================================
@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = (
        "visited_at",
        "path",
        "method",
        "ip_address",
        "location",
        "user",
    )
    list_filter = (
        "method",
        "location",
        "ip_address",
        "visited_at",
        "user",
    )
    search_fields = (
        "path",
        "ip_address",
        "user__username",
        "user__email",
        "user_agent",
        "referrer",
        "location",
    )
    date_hierarchy = "visited_at"
    ordering = ("-visited_at",)


# ============================================================
# SCRAPED MARKET SOURCE ADMIN
# ============================================================
@admin.register(ScrapedMarketSource)
class ScrapedMarketSourceAdmin(admin.ModelAdmin):
    list_display = (
        "source_name",
        "source_url",
        "sentiment_score",
        "processed",
        "scraped_at",
    )

    list_filter = (
        "processed",
        "scraped_at",
    )

    search_fields = (
        "source_name",
        "source_url",
        "extracted_text",
    )

    readonly_fields = (
        "scraped_at",
    )

    ordering = ("-scraped_at",)


# ============================================================
# COMPETITOR MARKET DATA ADMIN
# ============================================================
@admin.register(CompetitorMarketData)
class CompetitorMarketDataAdmin(admin.ModelAdmin):
    list_display = (
        "brand_name",
        "market_share_percentage",
        "market_status",
        "market_share_gap",
        "trend",
        "recorded_date",
    )

    list_filter = (
        "brand_name",
        "recorded_date",
        "trend__market_region",
        "trend__industry",
    )

    search_fields = (
        "brand_name",
        "trend__trend_title",
    )

    date_hierarchy = "recorded_date"
    ordering = ("-recorded_date",)

    readonly_fields = (
        "market_status",
        "market_share_gap",
    )

    def market_status(self, obj):
        return "Leader" if obj.market_share_percentage >= 50 else "Follower"

    def market_share_gap(self, obj):
        top = CompetitorMarketData.objects.filter(trend=obj.trend).aggregate(
            models.Max('market_share_percentage')
        )['market_share_percentage__max'] or 0
        return round(top - obj.market_share_percentage, 2)

    market_status.short_description = "Status"
    market_share_gap.short_description = "Gap to Leader"


# ============================================================
# MARKET INDICATOR ADMIN
# ============================================================
@admin.register(MarketIndicator)
class MarketIndicatorAdmin(admin.ModelAdmin):
    list_display = (
        "indicator_name",
        "indicator_category",
        "value",
        "unit",
        "status",
        "color_indicator",
        "trend",
        "recorded_date",
    )

    list_filter = (
        "indicator_category",
        "unit",
        "recorded_date",
        "trend__industry",
        "trend__market_region",
    )

    search_fields = (
        "indicator_name",
        "trend__trend_title",
    )

    date_hierarchy = "recorded_date"
    ordering = ("-recorded_date",)

    readonly_fields = (
        "status",
        "color_indicator",
        "rendered_data",
    )

    def status(self, obj):
        return "High" if obj.value > 50 else "Low"

    def color_indicator(self, obj):
        return format_html(
            '<span style="color:{};">●</span>',
            'red' if obj.value > 50 else 'green'
        )

    def rendered_data(self, obj):
        return f"{obj.value} {obj.unit}"

    status.short_description = "Status"
    color_indicator.short_description = "Indicator"
    rendered_data.short_description = "Rendered"


# ============================================================
# CUSTOMER PROFILE ADMIN (AGGREGATED)
# ============================================================
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'age_range',
        'gender',
        'location',
        'total_reviews',
        'average_food_score',
        'overall_average_score',
    )

    list_filter = (
        'age_range',
        'gender',
        'location',
        'employment_status',
        'eating_out_frequency',
        'preferred_brand',
        'created_at',
    )

    search_fields = (
        'full_name',
        'location',
        'preferred_brand',
    )

    ordering = ('-created_at',)
    readonly_fields = (
        'total_reviews',
        'average_food_score',
        'overall_average_score',
        'sentiment_display',
    )

    def total_reviews(self, obj):
        return obj.review_set.count()

    def average_food_score(self, obj):
        return obj.review_set.aggregate(
            models.Avg('food_value')
        )['food_value__avg'] or 0

    def overall_average_score(self, obj):
        return obj.review_set.aggregate(
            models.Avg('overall_weighted_score')
        )['overall_weighted_score__avg'] or 0

    def sentiment_display(self, obj):
        data = SentimentAnalysis.objects.filter(review__customer=obj)
        summary = data.values('sentiment_label').annotate(count=models.Count('id'))
        return ", ".join([f"{d['sentiment_label']}: {d['count']}" for d in summary])

    sentiment_display.short_description = "Sentiment Summary"


# ============================================================
# FAST FOOD BRAND ADMIN
# ============================================================
@admin.register(FastFoodBrand)
class FastFoodBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'location')
    list_filter = ('name', 'location')
    search_fields = ('name', 'branch', 'location')


# ============================================================
# REVIEW ADMIN
# ============================================================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'brand',
        'customer',
        'overall_weighted_score',
        'competitor_advantage',
        'nps_score',
        'created_at',
    )

    list_filter = ('brand', 'created_at', 'nps_score')
    search_fields = ('customer__full_name', 'brand__name', 'full_experience')
    ordering = ('-created_at',)
    readonly_fields = ('overall_weighted_score', 'competitor_advantage')


# ============================================================
# SENTIMENT ANALYSIS ADMIN
# ============================================================
@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'review',
        'vader_score',
        'bert_score',
        'final_sentiment_score',
        'sentiment_label',
        'analyzed_at',
    )

    list_filter = ('sentiment_label', 'analyzed_at')
    search_fields = ('review__full_experience',)
    ordering = ('-analyzed_at',)
    readonly_fields = (
        'vader_score',
        'bert_score',
        'final_sentiment_score',
        'sentiment_label',
        'analyzed_at',
    )


# ============================================================
# ENGAGEMENT METRIC ADMIN
# ============================================================
@admin.register(EngagementMetric)
class EngagementMetricAdmin(admin.ModelAdmin):
    list_display = (
        'customer',
        'review',
        'engagement_score',
        'loyalty_index',
        'recorded_month',
    )

    list_filter = ('recorded_month',)
    search_fields = ('customer__full_name',)
    ordering = ('-recorded_month',)
    readonly_fields = ('engagement_score', 'loyalty_index')


# ============================================================
# INVENTORY ITEM ADMIN
# ============================================================
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'supplier',
        'category',
        'quantity_in_stock',
        'reorder_level',
        'unit_cost',
        'selling_price',
        'is_active',
    )

    list_filter = (
        'category',
        'supplier',
        'is_active',
    )

    search_fields = (
        'sku',
        'name',
        'supplier__company_name',
    )

    ordering = ('quantity_in_stock',)
    readonly_fields = ('last_restocked', 'last_sold')


# ============================================================
# SUPPLIER PERFORMANCE ADMIN
# ============================================================
@admin.register(SupplierPerformanceScore)
class SupplierPerformanceScoreAdmin(admin.ModelAdmin):
    list_display = (
        'supplier',
        'final_score',
        'rating_category',
        'timeliness_score',
        'quantity_accuracy_score',
        'quality_score',
        'complaint_score',
        'consistency_score',
        'trust_index',
        'risk_index',
        'last_updated',
    )

    list_filter = ('rating_category', 'last_updated')
    search_fields = ('supplier__company_name',)
    ordering = ('-final_score',)
    readonly_fields = ('final_score', 'rating_category', 'last_updated')


# ============================================================
# SUPPLIER ADMIN (AGGREGATED)
# ============================================================
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'supplier_code',
        'name',
        'company_name',
        'contact_person',
        'phone',
        'location',
        'is_active',
        'average_performance_score',
        'average_delivery_status',
        'complaint_count',
        'sentiment_score',
    )

    list_filter = ('is_active', 'location', 'created_at')
    search_fields = ('supplier_code', 'name', 'company_name', 'contact_person', 'phone', 'email')
    ordering = ('name',)
    readonly_fields = (
        'average_performance_score',
        'average_delivery_status',
        'complaint_count',
        'sentiment_score',
    )

    def average_performance_score(self, obj):
        return obj.supplierperformancescore.final_score if hasattr(obj, 'supplierperformancescore') else 0

    def average_delivery_status(self, obj):
        total = obj.deliveries.count()
        if total == 0:
            return "No deliveries"
        on_time = obj.deliveries.filter(delivery_status='ON_TIME').count()
        return f"{(on_time / total) * 100:.2f}% on time"

    def complaint_count(self, obj):
        return obj.complaints.filter(resolved=False).count()

    def sentiment_score(self, obj):
        return obj.sentiments.aggregate(
            models.Avg('confidence_score')
        )['confidence_score__avg'] or 0

    average_performance_score.short_description = "Performance"
    average_delivery_status.short_description = "Delivery Rate"
    complaint_count.short_description = "Complaints"
    sentiment_score.short_description = "Sentiment"


# ============================================================
# DELIVERY ADMIN
# ============================================================
@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = (
        'supplier',
        'order_number',
        'invoice_number',
        'product_category',
        'quantity_ordered',
        'quantity_delivered',
        'delivery_status',
        'condition_status',
        'expected_delivery_date',
        'actual_delivery_date',
        'created_at',
    )

    list_filter = (
        'delivery_status',
        'condition_status',
        'product_category',
        'expected_delivery_date',
        'actual_delivery_date',
        'created_at',
    )

    search_fields = (
        'supplier__name',
        'order_number',
        'invoice_number',
        'vehicle_registration',
        'driver_name',
    )

    ordering = ('-actual_delivery_date',)
    readonly_fields = ('created_at',)


# ============================================================
# SUPPLIER REVIEW ADMIN
# ============================================================
@admin.register(SupplierReview)
class SupplierReviewAdmin(admin.ModelAdmin):
    list_display = (
        'supplier',
        'communication_score',
        'flexibility_score',
        'price_competitiveness_score',
        'documentation_score',
        'created_at',
    )

    list_filter = ('created_at',)
    search_fields = ('supplier__name', 'review_comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


# ============================================================
# COMPLAINT ADMIN
# ============================================================
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'severity_level', 'resolved', 'created_at')
    list_filter = ('resolved', 'severity_level', 'created_at')
    search_fields = ('supplier__name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(SupplierSentiment)
class SupplierSentimentAdmin(admin.ModelAdmin):
    # Columns to show in the list view
    list_display = ('supplier', 'sentiment_label', 'confidence_score', 'source_type', 'created_at')
    
    # Filter sidebar for quick navigation
    list_filter = ('sentiment_label', 'source_type', 'created_at')
    
    # Search box for supplier names or sentiment text
    search_fields = ('supplier__name', 'text', 'sentiment_label')
    
    # Default ordering (newest first)
    ordering = ('-created_at',)
    
    # Optional: Make confidence_score read-only if it's generated by AI
    readonly_fields = ('created_at',)