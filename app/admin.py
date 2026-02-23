from django.contrib import admin

from .models import *


class MarketIndicatorInline(admin.TabularInline):
    model = MarketIndicator
    extra = 0
    show_change_link = True

class CompetitorMarketDataInline(admin.TabularInline):
    model = CompetitorMarketData
    extra = 0
    show_change_link = True


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
        "start_period",
        "end_period",
        "created_at"
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

    readonly_fields = (
        "scraped_at",
        "created_at",
    )

    ordering = ("-start_period",)

    inlines = [MarketIndicatorInline, CompetitorMarketDataInline]

    fieldsets = (
        ("Basic Information", {
            "fields": (
                "industry",
                "market_region",
                "trend_title",
                "trend_summary"
            )
        }),
        ("Core Market Metrics", {
            "fields": (
                "overall_growth_rate",
                "market_size_value",
                "inflation_impact_index",
                "consumer_spending_index"
            )
        }),
        ("Risk & Stability", {
            "fields": (
                "risk_level",
                "political_risk_index",
                "economic_volatility_index",
                "supply_chain_stability_index"
            )
        }),
        ("Digital & Consumer Trends", {
            "fields": (
                "online_ordering_growth",
                "delivery_adoption_rate",
                "youth_demand_index"
            )
        }),
        ("Data Source & AI Analysis", {
            "fields": (
                "data_source",
                "source_url",
                "analysis_model",
                "confidence_score",
                "scraped_at"
            )
        }),
        ("Period", {
            "fields": (
                "start_period",
                "end_period"
            )
        }),
    )

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
    
    
    
    
@admin.register(ScrapedMarketSource)
class ScrapedMarketSourceAdmin(admin.ModelAdmin):

    list_display = (
        "source_name",
        "source_url",
        "sentiment_score",
        "processed",
        "scraped_at"
    )

    list_filter = (
        "processed",
        "scraped_at"
    )

    search_fields = (
        "source_name",
        "source_url",
        "extracted_text"
    )

    readonly_fields = (
        "scraped_at",
    )

    ordering = ("-scraped_at",)



@admin.register(CompetitorMarketData)
class CompetitorMarketDataAdmin(admin.ModelAdmin):

    list_display = (
        "brand_name",
        "market_share_percentage",
        "average_price",
        "revenue_estimate",
        "brand_growth_rate",
        "customer_satisfaction_index",
        "recorded_date",
        "trend"
    )

    list_filter = (
        "brand_name",
        "recorded_date",
        "trend__market_region",
        "trend__industry"
    )

    search_fields = (
        "brand_name",
        "trend__trend_title"
    )

    date_hierarchy = "recorded_date"

    ordering = ("-recorded_date",)



@admin.register(MarketIndicator)
class MarketIndicatorAdmin(admin.ModelAdmin):

    list_display = (
        "indicator_name",
        "indicator_category",
        "value",
        "unit",
        "recorded_date",
        "trend"
    )

    list_filter = (
        "indicator_category",
        "unit",
        "recorded_date",
        "trend__industry",
        "trend__market_region"
    )

    search_fields = (
        "indicator_name",
        "trend__trend_title"
    )

    date_hierarchy = "recorded_date"

    ordering = ("-recorded_date",)







# Customer Profile Admin
# ---------------------------------------
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age_range', 'gender', 'location', 'employment_status', 'eating_out_frequency', 'preferred_brand', 'created_at')
    list_filter = ('age_range', 'gender', 'location', 'employment_status', 'eating_out_frequency', 'preferred_brand', 'created_at')
    search_fields = ('full_name', 'location', 'preferred_brand')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


# ---------------------------------------
# Fast Food Brand Admin
# ---------------------------------------
@admin.register(FastFoodBrand)
class FastFoodBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'location')
    list_filter = ('name', 'location')
    search_fields = ('name', 'branch', 'location')


# ---------------------------------------
# Review Admin
# ---------------------------------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'brand', 'customer', 'overall_weighted_score',
        'competitor_advantage', 'nps_score', 'created_at'
    )
    list_filter = ('brand', 'created_at', 'nps_score')
    search_fields = ('customer__full_name', 'brand__name', 'full_experience')
    ordering = ('-created_at',)

    readonly_fields = ('overall_weighted_score', 'competitor_advantage')


# ---------------------------------------
# Sentiment Analysis Admin
# ---------------------------------------
@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ('review', 'vader_score', 'bert_score', 'final_sentiment_score', 'sentiment_label', 'analyzed_at')
    list_filter = ('sentiment_label', 'analyzed_at')
    search_fields = ('review__full_experience',)
    ordering = ('-analyzed_at',)
    readonly_fields = ('vader_score', 'bert_score', 'final_sentiment_score', 'sentiment_label', 'analyzed_at')


# ---------------------------------------
# Engagement Metric Admin
# ---------------------------------------
@admin.register(EngagementMetric)
class EngagementMetricAdmin(admin.ModelAdmin):
    list_display = ('customer', 'review', 'engagement_score', 'loyalty_index', 'recorded_month')
    list_filter = ('recorded_month',)
    search_fields = ('customer__full_name',)
    ordering = ('-recorded_month',)
    readonly_fields = ('engagement_score', 'loyalty_index')

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        'sku', 'name', 'supplier',
        'category', 'quantity_in_stock',
        'reorder_level', 'unit_cost',
        'selling_price', 'is_active'
    )

    list_filter = (
        'category', 'supplier', 'is_active'
    )

    search_fields = (
        'sku', 'name', 'supplier__business_name'
    )

    ordering = ('quantity_in_stock',)

    readonly_fields = (
        'last_restocked', 'last_sold'
    )




@admin.register(Benchmark)
class BenchmarkAdmin(admin.ModelAdmin):
    list_display = (
        'supplier', 'metric_name',
        'metric_value', 'industry_average',
        'percentile_rank', 'benchmark_score',
        'evaluation_period'
    )

    list_filter = (
        'metric_name', 'evaluation_period'
    )

    search_fields = (
        'supplier__business_name', 'metric_name'
    )

    ordering = ('-benchmark_score',)




@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('supplier_code', 'name', 'company_name', 'contact_person', 'phone', 'location', 'is_active', 'created_at')
    list_filter = ('is_active', 'location', 'created_at')
    search_fields = ('supplier_code', 'name', 'company_name', 'contact_person', 'phone', 'email')
    ordering = ('name',)
    readonly_fields = ('created_at',)


# -------------------------
# Delivery Admin
# -------------------------
@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'order_number', 'invoice_number', 'product_category', 'quantity_ordered', 'quantity_delivered', 'delivery_status', 'condition_status', 'expected_delivery_date', 'actual_delivery_date', 'created_at')
    list_filter = ('delivery_status', 'condition_status', 'product_category', 'expected_delivery_date', 'actual_delivery_date', 'created_at')
    search_fields = ('supplier__name', 'order_number', 'invoice_number', 'vehicle_registration', 'driver_name')
    ordering = ('-actual_delivery_date',)
    readonly_fields = ('created_at',)


# -------------------------
# Supplier Review Admin
# -------------------------
@admin.register(SupplierReview)
class SupplierReviewAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'communication_score', 'flexibility_score', 'price_competitiveness_score', 'documentation_score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('supplier__name', 'review_comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


# -------------------------
# Supplier Performance Score Admin
# -------------------------
@admin.register(SupplierPerformanceScore)
class SupplierPerformanceScoreAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'final_score', 'rating_category', 'timeliness_score', 'quantity_accuracy_score', 'quality_score', 'complaint_score', 'consistency_score', 'trust_index', 'risk_index', 'last_updated')
    list_filter = ('rating_category', 'last_updated')
    search_fields = ('supplier__name',)
    ordering = ('-final_score',)
    readonly_fields = ('final_score', 'last_updated')


# -------------------------
# Supplier Sentiment Admin
# -------------------------
@admin.register(SupplierSentiment)
class SupplierSentimentAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'source_type', 'sentiment_label', 'confidence_score', 'created_at')
    list_filter = ('source_type', 'sentiment_label', 'created_at')
    search_fields = ('supplier__name', 'text')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


# -------------------------
# Complaint Admin
# -------------------------
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'severity_level', 'resolved', 'created_at')
    list_filter = ('resolved', 'severity_level', 'created_at')
    search_fields = ('supplier__name', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)