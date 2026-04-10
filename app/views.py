from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils import timezone
from functools import wraps
import logging
from typing import Callable, Iterable, Optional

from django.shortcuts import render, redirect
from django.db.models import Avg
from .models import CustomerProfile, FastFoodBrand, Review, SentimentAnalysis, EngagementMetric
from .utils import analyze_sentiment  # see utils.py for Vader + BERT

from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
logger = logging.getLogger(__name__)
User = get_user_model()

from django.shortcuts import render, get_object_or_404
from django.db.models import Avg, Count
from .models import *


# views.py

from django.shortcuts import render
from django.db.models import (
    Count, Avg, Sum, F, Q, FloatField, ExpressionWrapper
)
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from .models import (
    VisitorLog, Supplier, Delivery, Complaint,
    SupplierPerformanceScore, InventoryItem,
    Customer, Review, SentimentAnalysis,
    MarketTrend
)

from django.shortcuts import render
from .models import Review, SentimentAnalysis, CustomerProfile
from django.db.models import Avg, Max, Min
from django.shortcuts import render
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from .models import InventoryItem, Delivery
from django.shortcuts import render
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth
from .models import InventoryItem, Delivery

OPENROUTER_API_KEY = getattr(settings, "OPENROUTER_API_KEY", "")
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL   = getattr(settings, "OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")




def admin_dashboard(request):
    now = timezone.now()
    last_30_days = now - timedelta(days=30)

    # =====================================
    # PLATFORM ANALYTICS
    # =====================================
    logs = VisitorLog.objects.filter(visited_at__gte=last_30_days)

    page_views = logs.count()
    unique_visitors = logs.values("ip_address").distinct().count()

    bounce_ips = (
        logs.values("ip_address")
        .annotate(count=Count("id"))
        .filter(count=1)
        .count()
    )

    bounce_rate = (bounce_ips / unique_visitors * 100) if unique_visitors else 0

    # =====================================
    # SUPPLIER ANALYTICS
    # =====================================
    total_suppliers = Supplier.objects.count()
    active_suppliers = Supplier.objects.filter(is_active=True).count()

    avg_supplier_score = SupplierPerformanceScore.objects.aggregate(
        avg=Avg("final_score")
    )["avg"] or 0

    high_risk_suppliers = SupplierPerformanceScore.objects.filter(
        risk_index__gt=70
    ).count()

    # =====================================
    # DELIVERY ANALYTICS
    # =====================================
    total_deliveries = Delivery.objects.count()

    on_time_rate = (
        Delivery.objects.filter(delivery_status="ON_TIME").count()
        / total_deliveries * 100
    ) if total_deliveries else 0

    damaged_rate = (
        Delivery.objects.filter(condition_status="DAMAGED").count()
        / total_deliveries * 100
    ) if total_deliveries else 0

    # =====================================
    # COMPLAINT ANALYTICS
    # =====================================
    total_complaints = Complaint.objects.count()
    unresolved_complaints = Complaint.objects.filter(resolved=False).count()

    # =====================================
    # INVENTORY ANALYTICS
    # =====================================
    total_skus = InventoryItem.objects.count()

    low_stock = InventoryItem.objects.filter(
        quantity_in_stock__lte=F("reorder_level")
    ).count()

    inventory_value = InventoryItem.objects.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("quantity_in_stock") * F("unit_cost"),
                output_field=FloatField()
            )
        )
    )["total"] or 0

    # =====================================
    # CUSTOMER ANALYTICS
    # =====================================
    total_customers = Customer.objects.count()

    avg_ltv = Customer.objects.aggregate(
        avg=Avg("lifetime_value")
    )["avg"] or 0

    avg_churn = Customer.objects.aggregate(
        avg=Avg("churn_probability")
    )["avg"] or 0

    # =====================================
    # REVIEW & SENTIMENT
    # =====================================
    total_reviews = Review.objects.count()

    avg_review_score = Review.objects.aggregate(
        avg=Avg("overall_weighted_score")
    )["avg"] or 0

    positive_sentiment = SentimentAnalysis.objects.filter(
        sentiment_label="Positive"
    ).count()

    total_sentiments = SentimentAnalysis.objects.count()

    sentiment_positive_rate = (
        positive_sentiment / total_sentiments * 100
    ) if total_sentiments else 0

    # =====================================
    # MARKET ANALYTICS
    # =====================================
    avg_market_growth = MarketTrend.objects.aggregate(
        avg=Avg("overall_growth_rate")
    )["avg"] or 0

    avg_market_risk = MarketTrend.objects.aggregate(
        avg=Avg("risk_level")
    )["avg"] or 0

    context = {

        # Platform
        "bounce_rate": round(bounce_rate, 2),
        "page_views": page_views,
        "unique_visitors": unique_visitors,

        # Supplier
        "total_suppliers": total_suppliers,
        "active_suppliers": active_suppliers,
        "avg_supplier_score": round(avg_supplier_score, 2),
        "high_risk_suppliers": high_risk_suppliers,

        # Delivery
        "on_time_rate": round(on_time_rate, 2),
        "damaged_rate": round(damaged_rate, 2),

        # Complaints
        "total_complaints": total_complaints,
        "unresolved_complaints": unresolved_complaints,

        # Inventory
        "total_skus": total_skus,
        "low_stock": low_stock,
        "inventory_value": round(inventory_value, 2),

        # Customer
        "total_customers": total_customers,
        "avg_ltv": round(float(avg_ltv), 2),
        "avg_churn": round(avg_churn, 2),

        # Review & Sentiment
        "total_reviews": total_reviews,
        "avg_review_score": round(avg_review_score, 2),
        "sentiment_positive_rate": round(sentiment_positive_rate, 2),

        # Market
        "avg_market_growth": round(avg_market_growth, 2),
        "avg_market_risk": round(avg_market_risk, 2),
    }

    return render(request, "dashboard.html", context)





from django.shortcuts import render
from django.db.models import Count, Avg, Sum
from django.db.models.functions import TruncMonth
import json

from .models import (
    VisitorLog, Supplier, SupplierPerformanceScore, SupplierSentiment,
    Customer, CustomerProfile, FastFoodBrand, Review, SentimentAnalysis,
    EngagementMetric, InventoryItem, Delivery, Complaint,
    SupplierReview, Benchmark, MarketTrend, MarketIndicator,
    ScrapedMarketSource, CompetitorMarketData, DecisionRecommendation
)


import json
from django.shortcuts import render
from django.db.models import Count, Avg, Sum


def dashboard(request):

    context = {}

    # -------------------------------------------------
    # VISITOR ANALYTICS
    # -------------------------------------------------

    context["total_visits"] = VisitorLog.objects.count()

    context["unique_visitors"] = (
        VisitorLog.objects.values("ip_address").distinct().count()
    )

    context["top_pages"] = (
        VisitorLog.objects.values("path")
        .annotate(visits=Count("id"))
        .order_by("-visits")[:10]
    )

    context["top_locations"] = (
        VisitorLog.objects.values("location")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    # -------------------------------------------------
    # SUPPLIER ANALYTICS
    # -------------------------------------------------

    context["total_suppliers"] = Supplier.objects.count()
    context["active_suppliers"] = Supplier.objects.filter(is_active=True).count()
    context["inactive_suppliers"] = Supplier.objects.filter(is_active=False).count()
    context["suppliers"] = Supplier.objects.all()

    # -------------------------------------------------
    # SUPPLIER PERFORMANCE
    # -------------------------------------------------

    scores = SupplierPerformanceScore.objects.select_related("supplier")

    context["supplier_scores"] = scores

    context["avg_supplier_score"] = scores.aggregate(
        avg=Avg("final_score")
    )["avg"]

    context["excellent_suppliers"] = scores.filter(
        rating_category="Excellent"
    ).count()

    context["good_suppliers"] = scores.filter(
        rating_category="Good"
    ).count()

    context["average_suppliers"] = scores.filter(
        rating_category="Average"
    ).count()

    context["poor_suppliers"] = scores.filter(
        rating_category="Poor"
    ).count()

    # -------------------------------------------------
    # SUPPLIER SENTIMENT ANALYSIS
    # -------------------------------------------------

    sentiment_counts = (
        SupplierSentiment.objects.values("sentiment_label")
        .annotate(count=Count("id"))
    )

    positive = neutral = negative = 0

    for s in sentiment_counts:
        if s["sentiment_label"] == "Positive":
            positive = s["count"]
        elif s["sentiment_label"] == "Neutral":
            neutral = s["count"]
        elif s["sentiment_label"] == "Negative":
            negative = s["count"]

    context["positive_sentiments"] = positive
    context["neutral_sentiments"] = neutral
    context["negative_sentiments"] = negative

    context["sentiments"] = SupplierSentiment.objects.select_related("supplier")[:100]

    # -------------------------------------------------
    # CUSTOMER ANALYTICS
    # -------------------------------------------------

    context["total_customers"] = Customer.objects.count()

    context["avg_lifetime_value"] = Customer.objects.aggregate(
        avg=Avg("lifetime_value")
    )["avg"]

    context["avg_churn"] = Customer.objects.aggregate(
        avg=Avg("churn_probability")
    )["avg"]

    context["avg_engagement"] = Customer.objects.aggregate(
        avg=Avg("engagement_score")
    )["avg"]

    # -------------------------------------------------
    # CUSTOMER CHURN CHART
    # -------------------------------------------------

    churn_labels = ["Low Risk", "Medium Risk", "High Risk"]

    low = Customer.objects.filter(churn_probability__lt=0.3).count()

    medium = Customer.objects.filter(
        churn_probability__gte=0.3,
        churn_probability__lt=0.7
    ).count()

    high = Customer.objects.filter(
        churn_probability__gte=0.7
    ).count()

    context["churn_labels"] = json.dumps(churn_labels)
    context["churn_values"] = json.dumps([low, medium, high])

    # -------------------------------------------------
    # CUSTOMER PROFILE ANALYTICS
    # -------------------------------------------------

    context["total_profiles"] = CustomerProfile.objects.count()

    context["profiles_by_location"] = (
        CustomerProfile.objects.values("location")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    # -------------------------------------------------
    # FAST FOOD BRAND ANALYTICS
    # -------------------------------------------------

    context["total_brands"] = FastFoodBrand.objects.count()
    context["brands"] = FastFoodBrand.objects.all()

    # -------------------------------------------------
    # REVIEW ANALYTICS
    # -------------------------------------------------

    context["total_reviews"] = Review.objects.count()

    context["avg_review_score"] = Review.objects.aggregate(
        avg=Avg("overall_weighted_score")
    )["avg"]

    context["reviews"] = Review.objects.select_related("brand", "customer")[:100]

    # -------------------------------------------------
    # ENGAGEMENT METRICS
    # -------------------------------------------------

    engagement = EngagementMetric.objects.select_related("customer")

    context["engagement_records"] = engagement.count()

    context["total_page_views"] = engagement.aggregate(
        total=Sum("page_views")
    )["total"]

    context["total_clicks"] = engagement.aggregate(
        total=Sum("clicks")
    )["total"]

    context["avg_loyalty_index"] = engagement.aggregate(
        avg=Avg("loyalty_index")
    )["avg"]

    # Engagement Calendar

    events = []

    for e in engagement:
        events.append({
            "title": f"{e.customer.full_name} Engagement",
            "start": e.recorded_month.strftime("%Y-%m-%d")
        })

    context["calendar_events"] = json.dumps(events)

    # -------------------------------------------------
    # INVENTORY ANALYTICS
    # -------------------------------------------------

    inventory = InventoryItem.objects.all()

    context["inventory_items"] = inventory
    context["inventory_count"] = inventory.count()

    context["low_stock_items"] = inventory.filter(
        quantity_in_stock__lte=5
    ).count()

    inventory_by_category = (
        inventory.values("category")
        .annotate(count=Count("id"))
    )

    context["inventory_chart_labels"] = json.dumps(
        [i["category"] for i in inventory_by_category]
    )

    context["inventory_chart_values"] = json.dumps(
        [i["count"] for i in inventory_by_category]
    )

    # -------------------------------------------------
    # DELIVERY ANALYTICS
    # -------------------------------------------------

    deliveries = Delivery.objects.select_related("supplier")

    context["deliveries"] = deliveries
    context["total_deliveries"] = deliveries.count()

    delivery_chart = (
        deliveries.values("delivery_status")
        .annotate(count=Count("id"))
    )

    context["delivery_labels"] = json.dumps(
        [d["delivery_status"] for d in delivery_chart]
    )

    context["delivery_values"] = json.dumps(
        [d["count"] for d in delivery_chart]
    )

    # -------------------------------------------------
    # COMPLAINT ANALYTICS
    # -------------------------------------------------

    complaints = Complaint.objects.select_related("supplier")

    context["complaints"] = complaints
    context["total_complaints"] = complaints.count()

    # -------------------------------------------------
    # MARKET TREND ANALYTICS
    # -------------------------------------------------

# -------------------------------------------------
# MARKET TREND ANALYTICS
# -------------------------------------------------

    trends = MarketTrend.objects.all()

    context["trends"] = trends
    context["market_trends"] = trends.count()

    trend_chart = (
        MarketTrend.objects.values("trend_title")
        .annotate(count=Count("id"))
    )

    context["trend_labels"] = json.dumps(
        [t["trend_title"] for t in trend_chart]
    )

    context["trend_values"] = json.dumps(
        [t["count"] for t in trend_chart]
    )
    # -------------------------------------------------
    # MARKET INDICATORS
    # -------------------------------------------------

    indicators = MarketIndicator.objects.all()

    context["market_indicators"] = indicators
    context["indicator_count"] = indicators.count()

    indicator_chart = (
        MarketIndicator.objects.values("indicator_name")
        .annotate(count=Count("id"))
    )

    context["indicator_labels"] = json.dumps(
        [i["indicator_name"] for i in indicator_chart]
    )

    context["indicator_values"] = json.dumps(
        [i["count"] for i in indicator_chart]
    )

    # -------------------------------------------------
    # COMPETITOR DATA
    # -------------------------------------------------

    competitors = CompetitorMarketData.objects.all()

    context["competitors"] = competitors
    context["competitor_count"] = competitors.count()

    # -------------------------------------------------
    # AI DECISION REPORTS
    # -------------------------------------------------

    decisions = DecisionRecommendation.objects.all()

    context["decision_reports"] = decisions
    context["decision_count"] = decisions.count()

    return render(request, "index.html", context)

def home_view(request):
    return render(request, "home.html")
# Supplier reviews page
def supplier_reviews(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    reviews = Review.objects.filter(supplier=supplier)
    return render(request, "supplier_reviews.html", {"supplier": supplier, "reviews": reviews})

# Customer reviews page
def customer_reviews(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    reviews = Review.objects.filter(customer=customer)
    return render(request, "customer_reviews.html", {"customer": customer, "reviews": reviews})

# Supplier management dashboard
def supplier_management(request):
    suppliers = Supplier.objects.all().order_by("name")
    return render(request, "supplier_manage.html", {"suppliers": suppliers})

from django.db.models.functions import TruncDate
from django.db.models import Count, Q

def customerdashboard(request):
    reviews = Review.objects.select_related('customer','brand')
    sentiments = SentimentAnalysis.objects.select_related('review__customer','review__brand')
    customers = CustomerProfile.objects.all()

    total_entries = reviews.count()
    total_customers = customers.count()

    highest_positive = sentiments.aggregate(Max('final_sentiment_score'))['final_sentiment_score__max']
    highest_negative = sentiments.aggregate(Min('final_sentiment_score'))['final_sentiment_score__min']


    # SENTIMENT DISTRIBUTION
    sentiment_counts = sentiments.values('sentiment_label').annotate(count=Count('id'))

    positive = 0
    neutral = 0
    negative = 0

    positive = sentiments.filter(final_sentiment_score__gt=0).count()

    negative = sentiments.filter(final_sentiment_score__lt=0).count()

    neutral = sentiments.filter(final_sentiment_score=0).count()

    print(negative)
    # REVIEWS OVER TIME
    review_trend = reviews.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')


    trend_dates = [str(r['date']) for r in review_trend]
    trend_counts = [r['count'] for r in review_trend]


    context = {

        "reviews": reviews,
        "sentiments": sentiments,
        "customers": customers,

        "total_entries": total_entries,
        "total_customers": total_customers,
        "highest_positive": highest_positive,
        "highest_negative": highest_negative,

        # chart data
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "trend_dates": trend_dates,
        "trend_counts": trend_counts,
    }
    return render(request, "customerdashboard.html",context)


from django.db.models import Avg, Count
from .models import *

def supplierdashboard(request):

    total_suppliers = Supplier.objects.count()

    avg_score = SupplierPerformanceScore.objects.aggregate(
        Avg("final_score")
    )["final_score__avg"]

    total_deliveries = Delivery.objects.count()

    total_complaints = Complaint.objects.count()

    supplier_scores = SupplierPerformanceScore.objects.select_related("supplier").order_by("-final_score")

    best_supplier = supplier_scores.first().supplier.name

    risky_supplier = SupplierPerformanceScore.objects.order_by("-risk_index").first().supplier.name

    complaint_supplier = Complaint.objects.values("supplier__name").annotate(
        c=Count("id")
    ).order_by("-c").first()

    context = {
        "total_suppliers": total_suppliers,
        "avg_score": round(avg_score,2),
        "total_deliveries": total_deliveries,
        "total_complaints": total_complaints,
        "supplier_scores": supplier_scores,
        "best_supplier": best_supplier,
        "risky_supplier": risky_supplier,
            "suppliers": Supplier.objects.all(),
    "deliveries": Delivery.objects.all(),
    "reviews": SupplierReview.objects.all(),
    "complaints": Complaint.objects.all(),
        "complaint_supplier": complaint_supplier["supplier__name"],
    }

    return render(request,"supplierdashboard.html",context)
def inventory(request):
    inventory = InventoryItem.objects.select_related("supplier")
    deliveries = Delivery.objects.select_related("supplier")

    # INVENTORY STATS
    total_products = inventory.count()

    total_stock = inventory.aggregate(
        Sum("quantity_in_stock")
    )["quantity_in_stock__sum"] or 0

    low_stock_items = inventory.filter(
        quantity_in_stock__lte=F("reorder_level")
    ).count()

    active_products = inventory.filter(is_active=True).count()

    inactive_products = inventory.filter(is_active=False).count()

    inventory_value = inventory.aggregate(
        total=Sum(
            ExpressionWrapper(
                F("quantity_in_stock") * F("unit_cost"),
                output_field=DecimalField()
            )
        )
    )["total"] or 0

    avg_selling_price = inventory.aggregate(
        Avg("selling_price")
    )["selling_price__avg"] or 0

    # DELIVERY STATS
    total_deliveries = deliveries.count()

    on_time_deliveries = deliveries.filter(
        delivery_status="ON_TIME"
    ).count()

    late_deliveries = deliveries.filter(
        delivery_status="LATE"
    ).count()

    early_deliveries = deliveries.filter(
        delivery_status="EARLY"
    ).count()

    damaged_goods = deliveries.filter(
        condition_status="DAMAGED"
    ).count()

    partial_deliveries = deliveries.filter(
        condition_status="PARTIAL"
    ).count()

    documentation_issues = deliveries.filter(
        documentation_complete=False
    ).count()

    # SUPPLIER RANKING
    top_suppliers = deliveries.values(
        "supplier__name"
    ).annotate(
        deliveries_count=Count("id")
    ).order_by("-deliveries_count")[:5]

    context = {

        "inventory": inventory,
        "deliveries": deliveries,

        # inventory stats
        "total_products": total_products,
        "total_stock": total_stock,
        "low_stock_items": low_stock_items,
        "active_products": active_products,
        "inactive_products": inactive_products,
        "inventory_value": inventory_value,
        "avg_selling_price": avg_selling_price,

        # delivery stats
        "total_deliveries": total_deliveries,
        "on_time_deliveries": on_time_deliveries,
        "late_deliveries": late_deliveries,
        "early_deliveries": early_deliveries,
        "damaged_goods": damaged_goods,
        "partial_deliveries": partial_deliveries,
        "documentation_issues": documentation_issues,

        "top_suppliers": top_suppliers,
    }
    return render(request, "inventory.html", context)

def audit(request):

    engagement = EngagementMetric.objects.all()
    visitors = VisitorLog.objects.all()

    context = {

        "engagement_metrics": engagement,
        "visitor_logs": visitors,

        "total_visitors": visitors.count(),

        "total_page_views": engagement.aggregate(
            Sum("page_views")
        )["page_views__sum"] or 0,

        "total_clicks": engagement.aggregate(
            Sum("clicks")
        )["clicks__sum"] or 0,

        "total_messages": engagement.aggregate(
            Sum("messages_sent")
        )["messages_sent__sum"] or 0,
    }

    return render(request, "audit.html", context)
def customer_review_view(request):
    # ---------------------------------
    # 1️⃣ TRACK PAGE VIEW AUTOMATICALLY
    # ---------------------------------
    if "page_views" not in request.session:
        request.session["page_views"] = 0
    request.session["page_views"] += 1

    # Track session start time
    if "start_time" not in request.session:
        request.session["start_time"] = str(timezone.now())

    if request.method == "POST":
        try:
            # Calculate time spent
            start_time = timezone.datetime.fromisoformat(request.session["start_time"])
            time_spent = (timezone.now() - start_time).total_seconds()

            # Count submission as click
            clicks = 1  

            # -------------------------------
            # Save Customer
            # -------------------------------
            customer = CustomerProfile.objects.create(
                full_name=request.POST.get("full_name"),
                age_range=request.POST.get("age_range"),
                gender=request.POST.get("gender"),
                location=request.POST.get("location"),
                employment_status=request.POST.get("employment_status"),
                eating_out_frequency=request.POST.get("eating_out_frequency"),
                preferred_brand=request.POST.get("preferred_brand")
            )

            # -------------------------------
            # Save Brand
            # -------------------------------
            brand, _ = FastFoodBrand.objects.get_or_create(
                name=request.POST.get("restaurant_name"),
                branch=request.POST.get("branch")
            )

            # -------------------------------
            # Save Review
            # -------------------------------
            review = Review.objects.create(
                customer=customer,
                brand=brand,
                taste=int(request.POST.get("taste") or 0),
                freshness=int(request.POST.get("freshness") or 0),
                portion_size=int(request.POST.get("portion_size") or 0),
                presentation=int(request.POST.get("presentation") or 0),
                menu_variety=int(request.POST.get("menu_variety") or 0),
                food_value=int(request.POST.get("food_value") or 0),
                staff_friendliness=int(request.POST.get("staff_friendliness") or 0),
                professionalism=int(request.POST.get("professionalism") or 0),
                order_accuracy=int(request.POST.get("order_accuracy") or 0),
                waiting_time=int(request.POST.get("waiting_time") or 0),
                problem_resolution=int(request.POST.get("problem_resolution") or 0),
                cleanliness=int(request.POST.get("cleanliness") or 0),
                ambience=int(request.POST.get("ambience") or 0),
                seating=int(request.POST.get("seating") or 0),
                hygiene=int(request.POST.get("hygiene") or 0),
                affordability=int(request.POST.get("affordability") or 0),
                pricing_fairness=int(request.POST.get("pricing_fairness") or 0),
                promotions=int(request.POST.get("promotions") or 0),
                brand_reputation=int(request.POST.get("brand_reputation") or 0),
                food_trust=int(request.POST.get("food_trust") or 0),
                nps_score=int(request.POST.get("nps_score") or 0),
                vs_chickeninn=request.POST.get("vs_chickeninn"),
                vs_kfc=request.POST.get("vs_kfc"),
                vs_galitos=request.POST.get("vs_galitos"),
                full_experience=request.POST.get("full_experience"),
                improvement_suggestions=request.POST.get("improvement_suggestions")
            )

            # -------------------------------
            # SENTIMENT ANALYSIS
            # -------------------------------
            vader_score, bert_score = analyze_sentiment(review.full_experience or "")
            final_sentiment = (vader_score + bert_score) / 2
            sentiment_label = "Positive" if final_sentiment >= 0 else "Negative"

            SentimentAnalysis.objects.create(
                review=review,
                vader_score=vader_score,
                bert_score=bert_score,
                final_sentiment_score=final_sentiment,
                sentiment_label=sentiment_label
            )

            # -------------------------------
            # AUTO CALCULATE ENGAGEMENT
            # -------------------------------
            page_views = request.session.get("page_views", 1)
            engagement_score = (
                (page_views * 0.2) +
                (clicks * 0.3) +
                (time_spent * 0.001)
            )
            loyalty_index = (
                (review.nps_score * 0.6) +
                (engagement_score * 0.4)
            )

            EngagementMetric.objects.create(
                customer=customer,
                review=review,
                page_views=page_views,
                clicks=clicks,
                messages_sent=0,
                support_tickets=0,
                engagement_score=engagement_score,
                loyalty_index=loyalty_index
            )

            # Clear session tracking
            request.session.flush()

            # -------------------------------
            # ADD SUCCESS ALERT
            # -------------------------------
            messages.success(request, "Thank you! Your review has been submitted successfully.")

            return redirect("customer")

        except Exception as e:
            # -------------------------------
            # ADD ERROR ALERT
            # -------------------------------
            messages.error(request, f"An error occurred while submitting your review: {str(e)}")

    return render(request, "customer.html")

# Supplier sentiments page
def supplier_sentiments(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    sentiments = SentimentAnalysis.objects.filter(supplier=supplier)
    return render(request, "supplier_sentiments.html", {"supplier": supplier, "sentiments": sentiments})

# Customer sentiments page
def customer_sentiments(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    sentiments = SentimentAnalysis.objects.filter(customer=customer)
    return render(request, "customer_sentiments.html", {"customer": customer, "sentiments": sentiments})

# Customer engagement analytics
def customer_engagement(request):
    engagement_data = EngagementMetric.objects.all()
    return render(request, "customer_engagement.html", {"engagement_data": engagement_data})

# Store Inventory page
def store_inventory(request):
    inventory = InventoryItem.objects.all()
    return render(request, "store_inventory.html", {"inventory": inventory})

# Report & decision recommendations page

def call_openrouter(system_prompt: str, user_prompt: str, max_tokens: int = 900) -> str:
    """Call OpenRouter and return the assistant text, or an empty string on failure."""
    if not OPENROUTER_API_KEY:
        return ""
    try:
        resp = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://kpifastfood.app",
                "X-Title": "KPI Fastfood Analytics",
            },
            json={
                "model": OPENROUTER_MODEL,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""
 
 
def build_data_snapshot() -> dict:
    """Aggregate key metrics from the database into a single dict for the AI prompt."""
    # Supplier stats
    supplier_total   = Supplier.objects.filter(is_active=True).count()
    perf_scores      = SupplierPerformanceScore.objects.select_related("supplier")
    avg_final_score  = perf_scores.aggregate(a=Avg("final_score"))["a"] or 0
    avg_risk         = perf_scores.aggregate(a=Avg("risk_index"))["a"] or 0
    avg_trust        = perf_scores.aggregate(a=Avg("trust_index"))["a"] or 0
    high_risk_count  = perf_scores.filter(risk_index__gte=70).count()
    rating_dist      = {
        cat: perf_scores.filter(rating_category=cat).count()
        for cat in ("Excellent", "Good", "Average", "Poor")
    }
 
    # Delivery stats
    total_deliveries  = Delivery.objects.count()
    on_time_count     = Delivery.objects.filter(delivery_status="ON_TIME").count()
    late_count        = Delivery.objects.filter(delivery_status="LATE").count()
    damaged_count     = Delivery.objects.filter(condition_status="DAMAGED").count()
    on_time_rate      = round((on_time_count / total_deliveries * 100) if total_deliveries else 0, 1)
 
    # Complaints
    total_complaints    = Complaint.objects.count()
    unresolved          = Complaint.objects.filter(resolved=False).count()
    high_severity       = Complaint.objects.filter(severity_level__gte=4).count()
 
    # Customer reviews
    review_count        = Review.objects.count()
    avg_weighted_score  = Review.objects.aggregate(a=Avg("overall_weighted_score"))["a"] or 0
    avg_nps             = Review.objects.aggregate(a=Avg("nps_score"))["a"] or 0
 
    # Inventory
    low_stock_count     = InventoryItem.objects.filter(
        quantity_in_stock__lte=F("reorder_level"), is_active=True
    ).count()
 
    # Top suppliers by review volume
    top_suppliers = list(
        Supplier.objects.annotate(rc=Count("reviews"))
        .order_by("-rc")[:5]
        .values("name", "rc")
    )
 
    return {
        "supplier_total":    supplier_total,
        "avg_final_score":   round(avg_final_score, 1),
        "avg_risk_index":    round(avg_risk, 1),
        "avg_trust_index":   round(avg_trust, 1),
        "high_risk_suppliers": high_risk_count,
        "rating_distribution": rating_dist,
        "total_deliveries":  total_deliveries,
        "on_time_rate":      on_time_rate,
        "late_deliveries":   late_count,
        "damaged_deliveries": damaged_count,
        "total_complaints":  total_complaints,
        "unresolved_complaints": unresolved,
        "high_severity_complaints": high_severity,
        "customer_review_count": review_count,
        "avg_weighted_customer_score": round(avg_weighted_score, 1),
        "avg_nps": round(avg_nps, 1),
        "low_stock_items": low_stock_count,
        "top_suppliers_by_reviews": top_suppliers,
    }
 
 
def get_ai_insights(snapshot: dict) -> dict:
    """
    Ask the AI for four structured insight blocks.
    Returns a dict with keys: summary, risks, opportunities, actions.
    Falls back to empty strings when OpenRouter is unavailable.
    """
    SYSTEM = (
        "You are an expert supply-chain and restaurant operations analyst. "
        "Respond ONLY with a JSON object — no markdown, no preamble. "
        "Keys: summary (2 sentences), risks (list of 3 strings), "
        "opportunities (list of 3 strings), actions (list of 4 strings). "
        "Be specific and reference the numbers provided."
    )
    USER = (
        f"Here is today's KPI snapshot for a fast-food supply chain operation:\n"
        f"{json.dumps(snapshot, indent=2)}\n\n"
        "Provide a concise strategic analysis."
    )
    raw = call_openrouter(SYSTEM, USER, max_tokens=700)
    if not raw:
        return {"summary": "", "risks": [], "opportunities": [], "actions": []}
    try:
        # Strip any accidental markdown fences
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(clean)
    except (json.JSONDecodeError, KeyError):
        return {"summary": raw, "risks": [], "opportunities": [], "actions": []}
 
 
# ─────────────────────────────────────────────
# Main view
# ─────────────────────────────────────────────
def report_and_recommendations(request):
    snapshot = build_data_snapshot()
    ai       = get_ai_insights(snapshot)
 
    avg_supplier_rating = Review.objects.aggregate(
        avg=Avg("overall_weighted_score")
    )["avg"] or 0
 
    top_performers = Supplier.objects.annotate(
        review_count=Count("reviews")
    ).order_by("-review_count")[:5]
 
    decision_reports = DecisionRecommendation.objects.order_by("-created_at")[:12]
 
    context = {
        # existing
        "avg_supplier_rating":  round(avg_supplier_rating, 1),
        "top_performers":       top_performers,
        "decision_count":       decision_reports.count(),
        "decision_reports":     decision_reports,
 
        # new AI + snapshot
        "snapshot":             snapshot,
        "ai_summary":           ai.get("summary", ""),
        "ai_risks":             ai.get("risks", []),
        "ai_opportunities":     ai.get("opportunities", []),
        "ai_actions":           ai.get("actions", []),
        "ai_available":         bool(OPENROUTER_API_KEY),
        "generated_at":         timezone.now(),
    }
 
    return render(request, "reports.html", context)
# Performance benchmark page
def performance_benchmark(request):
    benchmarks = Benchmark.objects.order_by("-score")
    return render(request, "benchmark.html", {"benchmarks": benchmarks})

# Market industry and trends page
def market_industry_trends(request):
    trends = MarketTrend.objects.order_by("-date_recorded")
    return render(request, "market_trends.html", {"trends": trends})



# ===== Authentication & Session Handling =====

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 minutes


def _get_login_cache_key(identifier: str, ip: str) -> str:
    """
    Build a cache key for tracking login attempts.
    Uses a combination of user identifier (username/email) and IP.
    """
    safe_identifier = identifier or "anonymous"
    safe_ip = ip or "unknown_ip"
    return f"login_attempts:{safe_identifier}:{safe_ip}"


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Handle user login via username or email + password.

    Expects a POST with:
      - identifier: username or email
      - password: plain text password

    Template:
      - app/login.html (customize as needed)
    """
    if request.user.is_authenticated:
        print(request.user)
        return redirect("dashboard")

    ip = request.META.get("REMOTE_ADDR", "")

    if request.method == "POST":
        identifier = (request.POST.get("identifier") or "").strip()
        password = request.POST.get("password") or ""

        cache_key = _get_login_cache_key(identifier, ip)
        attempts_info = cache.get(cache_key, {"count": 0, "locked_until": None})

        # Check lockout
        locked_until = attempts_info.get("locked_until")
        now = timezone.now()
        if locked_until and now < locked_until:
            remaining = int((locked_until - now).total_seconds())
            messages.error(
                request,
                f"Too many failed attempts. Please try again in {remaining} seconds.",
            )
            logger.warning(
                "Login attempt during lockout",
                extra={"identifier": identifier, "ip": ip},
            )
            return render(request, "app/login.html", status=403)

        user = None

        # First try identifier as username
        user = authenticate(request, username=identifier, password=password)

        # If that fails, try treating identifier as email
        if user is None:
            try:
                email_user = User.objects.get(email__iexact=identifier)
                user = authenticate(
                    request, username=email_user.get_username(), password=password
                )
            except User.DoesNotExist:
                user = None

        if user is not None and user.is_active:
            # Successful login: reset attempts & create session
            cache.delete(cache_key)
            auth_login(request, user)

            logger.info(
                "User logged in",
                extra={"user_id": user.id, "username": user.get_username(), "ip": ip},
            )

            messages.success(request, "Login successful.")
            next_url = (
                request.POST.get("next")
                or request.GET.get("next")
                or settings.LOGIN_REDIRECT_URL
                or "dashboard"
            )
            return redirect(next_url)

        # Failed login: increment attempts
        attempts = attempts_info.get("count", 0) + 1
        lockout_until = None
        if attempts >= MAX_LOGIN_ATTEMPTS:
            lockout_until = timezone.now() + timezone.timedelta(seconds=LOCKOUT_SECONDS)
            messages.error(
                request,
                "Too many failed attempts. Your account is temporarily locked. "
                "Please try again later.",
            )
            logger.warning(
                "User locked out due to failed logins",
                extra={
                    "identifier": identifier,
                    "ip": ip,
                    "attempts": attempts,
                },
            )
        else:
            messages.error(request, "Invalid credentials. Please try again.")

        cache.set(
            cache_key,
            {"count": attempts, "locked_until": lockout_until},
            timeout=LOCKOUT_SECONDS,
        )

        logger.warning(
            "Failed login attempt",
            extra={"identifier": identifier, "ip": ip, "attempts": attempts},
        )

    # GET or fall-through after POST
    return render(request, "login.html")


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Log the current user out and destroy the session.
    """
    ip = request.META.get("REMOTE_ADDR", "")
    user = request.user

    logger.info(
        "User logged out",
        extra={
            "user_id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
            "ip": ip,
        },
    )

    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# ===== Role-Based Access Control (RBAC) =====

def role_required(
    roles: Optional[Iterable[str]] = None,
    groups: Optional[Iterable[str]] = None,
    redirect_field_name: str = "next",
) -> Callable:
    """
    Decorator to restrict access based on user role/group.

    Usage examples:

    @role_required(roles=["admin"])
    def my_view(...):
        ...

    @role_required(groups=["managers", "staff"])
    def other_view(...):
        ...

    This implementation uses:
      - user.is_superuser as implicit "admin"
      - Django auth groups (user.groups)
      - OPTIONAL custom 'role' attribute on the user model (string)
    """

    if roles is not None:
        roles = set(roles)
    if groups is not None:
        groups = set(groups)

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not request.user.is_authenticated:
                # Delegate to login page
                from django.contrib.auth.views import redirect_to_login

                return redirect_to_login(request.get_full_path(), "login", redirect_field_name)

            user = request.user

            # Superusers bypass all checks
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Check custom 'role' attribute if present
            if roles:
                user_role = getattr(user, "role", None)
                if user_role in roles:
                    return view_func(request, *args, **kwargs)

            # Check Django auth groups
            if groups:
                user_groups = set(user.groups.values_list("name", flat=True))
                if user_groups.intersection(groups):
                    return view_func(request, *args, **kwargs)

            logger.warning(
                "Access denied due to insufficient role/group",
                extra={
                    "user_id": user.id,
                    "username": user.get_username(),
                    "required_roles": list(roles or []),
                    "required_groups": list(groups or []),
                },
            )

            # You can customize this to redirect to a dedicated 403 page
            return HttpResponseForbidden("You do not have permission to access this resource.")

        return _wrapped_view

    return decorator


# ===== Example Protected Views =====

@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    Basic authenticated dashboard.
    """
    return render(request, "index.html")


@role_required(roles=["admin"], groups=["Admins"])
def admin_dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    Admin-only dashboard for system-wide configuration and user/role management.
    Allows:
      - user.is_superuser, OR
      - user.role == 'admin', OR
      - membership in 'Admins' Django auth group.
    """
    return render(request, "app/admin_dashboard.html")


@role_required(roles=["manager", "analyst", "procurement"], groups=["Analysts", "Managers"])
def insights_view(request: HttpRequest) -> HttpResponse:
    """
    Supplier insights dashboard (trends, surveys, sentiment, delivery performance).
    Example roles/groups:
      - roles: manager, analyst, procurement
      - groups: Analysts, Managers
    """
    return render(request, "app/insights.html")


@role_required(roles=["procurement", "inventory"], groups=["Procurement"])
def inventory_view(request: HttpRequest) -> HttpResponse:
    """
    Inventory management and supplier rating workflows.
    """
    return render(request, "app/inventory.html")





# ----------------------------
# 1️⃣ Supplier Registration
# ----------------------------
def supplier_register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        company_name = request.POST.get("company_name")
        supplier_code = request.POST.get("supplier_code")
        contact_person = request.POST.get("contact_person")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        location = request.POST.get("location")
        is_active = request.POST.get("is_active") == "on"

        if not name or not supplier_code:
            messages.error(request, "Name and Supplier Code are required!")
            return redirect("supplier_register")

        Supplier.objects.create(
            name=name,
            company_name=company_name,
            supplier_code=supplier_code,
            contact_person=contact_person,
            phone=phone,
            email=email,
            location=location,
            is_active=is_active,
            created_at=timezone.now()
        )
        messages.success(request, f"Supplier {name} registered successfully!")
        return redirect("supplier_register")

    return render(request, "supplierregistration.html", {"page_title": "Supplier Registration"})


# ----------------------------
# 2️⃣ Delivery Recording
# ----------------------------
def record_delivery(request):
    suppliers = Supplier.objects.filter(is_active=True)

    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        order_number = request.POST.get("order_number")
        invoice_number = request.POST.get("invoice_number")
        product_category = request.POST.get("product_category")
        product_name = request.POST.get("product_name")
        sku = request.POST.get("sku")
        quantity_ordered = float(request.POST.get("quantity_ordered") or 0)
        quantity_delivered = float(request.POST.get("quantity_delivered") or 0)
        delivery_status = request.POST.get("delivery_status")
        condition_status = request.POST.get("condition_status")
        vehicle_registration = request.POST.get("vehicle_registration")
        driver_name = request.POST.get("driver_name")
        expected_delivery_date = request.POST.get("expected_delivery_date")
        actual_delivery_date = request.POST.get("actual_delivery_date")
        delivery_comment = request.POST.get("delivery_comment", "")

        supplier = Supplier.objects.get(id=supplier_id)

        # Save delivery
        delivery = Delivery.objects.create(
            supplier=supplier,
            order_number=order_number,
            invoice_number=invoice_number,
            product_category=product_category,
            quantity_ordered=quantity_ordered,
            quantity_delivered=quantity_delivered,
            delivery_status=delivery_status,
            condition_status=condition_status,
            vehicle_registration=vehicle_registration,
            driver_name=driver_name,
            expected_delivery_date=expected_delivery_date,
            actual_delivery_date=actual_delivery_date,
            created_at=timezone.now()
        )

        # Update or create inventory item
        if sku and product_name:
            inventory_item, created = InventoryItem.objects.get_or_create(
                supplier=supplier,
                sku=sku,
                defaults={
                    "name": product_name,
                    "category": product_category,
                    "quantity_in_stock": quantity_delivered,
                    "unit_cost": 0,  # you can modify to accept from form
                    "selling_price": 0,
                    "warehouse_location": "Default Warehouse",
                    "last_restocked": timezone.now()
                }
            )
            if not created:
                # Update existing stock
                inventory_item.quantity_in_stock += quantity_delivered
                inventory_item.last_restocked = timezone.now()
                inventory_item.save()

        # Analyze delivery comment sentiment
        if delivery_comment:
            vader, bert= analyze_sentiment(delivery_comment)
            final_score=(vader)
            SupplierSentiment.objects.create(
                supplier=supplier,
                source_type="delivery",
                source_id=delivery.id,
                text=delivery_comment,
                sentiment_label =vader,
                confidence_score=final_score
            )

        # Update supplier performance
        perf, _ = SupplierPerformanceScore.objects.get_or_create(supplier=supplier)
        #perf.update_from_delivery(delivery)
        #perf.update_from_sentiments()

        messages.success(request, f"Delivery for {supplier.name} recorded successfully!")
        return redirect("delivery")

    return render(request, "delivery_form.html", {
        "suppliers": suppliers,
        "page_title": "Record Supplier Delivery"
    })
# ----------------------------
# 3️⃣ Supplier Review
# ----------------------------
def supplier_review(request):
    suppliers = Supplier.objects.filter(is_active=True)

    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        communication_score = float(request.POST.get("communication_score") or 0)
        flexibility_score = float(request.POST.get("flexibility_score") or 0)
        documentation_score = float(request.POST.get("documentation_score") or 0)
        pricing_score = float(request.POST.get("pricing_score") or 0)
        review_comment = request.POST.get("review_comment", "")

        supplier = Supplier.objects.get(id=supplier_id)

        # Save review
        review = SupplierReview.objects.create(
            supplier=supplier,
            communication_score=communication_score,
            flexibility_score=flexibility_score,
            documentation_score=documentation_score,
            price_competitiveness_score =pricing_score,
            review_comment=review_comment,
            created_at=timezone.now()
        )

        # Analyze review sentiment
        if review_comment:
            vader, bert = analyze_sentiment(review_comment)
            final_score=(vader)
            SupplierSentiment.objects.create(
                supplier=supplier,
                source_type="review",
                source_id=review.id,
                text=review_comment,
                sentiment_label =vader,
                confidence_score=final_score
            )

        # Update supplier performance
        perf= SupplierPerformanceScore.objects.get_or_create(supplier=supplier)
        # perf.update_from_review(review)
        # perf.update_from_sentiments()
        messages.success(request, f"Review for {supplier.name} recorded successfully!")
        return redirect("supplier_review")

    return render(request, "supplier_review.html", {
        "suppliers": suppliers,
        "page_title": "Supplier Review"
    })


# ----------------------------
# 4️⃣ Complaint Logging
# ----------------------------
def record_complaint(request):
    suppliers = Supplier.objects.filter(is_active=True)

    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        description = request.POST.get("description", "")
        supplier = Supplier.objects.get(id=supplier_id)

        complaint = Complaint.objects.create(
            supplier=supplier,
            description=description,
            created_at=timezone.now()
        )

        # Negative sentiment from complaint
        if description:
            vader, bert= analyze_sentiment(description)
            final_score=vader
            final_score = min(final_score, 0)  # ensure negative
            SupplierSentiment.objects.create(
                supplier=supplier,
                source_type="complaint",
                source_id=complaint.id,
                text=description,
               sentiment_label =vader,
                confidence_score=final_score
            )

        # Update supplier performance
        perf, _ = SupplierPerformanceScore.objects.get_or_create(supplier=supplier)
        # perf.update_from_complaint(complaint)
        # perf.update_from_sentiments()
        messages.success(request, f"Complaint for {supplier.name} recorded successfully!")
        return redirect("supplier_complaint")

    return render(request, "complaint_form.html", {
        "suppliers": suppliers,
        "page_title": "Record Supplier Complaint"
    })