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
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from functools import wraps
import logging
import json
import re
import requests
from typing import Callable, Iterable, Optional
from datetime import timedelta

from django.db.models import (
    Avg, Count, Sum, Max, Min, F, Q,
    FloatField, ExpressionWrapper, DecimalField
)
from django.db.models.functions import TruncMonth, TruncDate, Coalesce

from .models import (
    VisitorLog, Supplier, Delivery, Complaint,
    SupplierPerformanceScore, InventoryItem,
    Customer, Review, SentimentAnalysis,
    MarketTrend, SupplierSentiment, SupplierReview,
    CustomerProfile, FastFoodBrand, EngagementMetric,
    MarketIndicator, ScrapedMarketSource, CompetitorMarketData,
    DecisionRecommendation, Benchmark
)
from .utils import analyze_sentiment

logger = logging.getLogger(__name__)
User = get_user_model()

OPENROUTER_API_KEY = getattr(settings, "OPENROUTER_API_KEY", "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")
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL   = getattr(settings, "OPENROUTER_MODEL", "openai/gpt-4o")


# ─────────────────────────────────────────────
# EMAIL HELPERS
# ─────────────────────────────────────────────

def send_html_email(subject, template_name, context, recipient_list):
    """Send an HTML email. Silently logs failures so they never break a form POST."""
    try:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@kpifastfood.app")
        html_body  = render_to_string(template_name, context)
        # Plain-text fallback (strip tags crudely)
        text_body  = re.sub(r"<[^>]+>", " ", html_body)

        msg = EmailMultiAlternatives(subject, text_body, from_email, recipient_list)
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
    except Exception as e:
        logger.error("Email send failed [%s]: %s", template_name, e)


# ─────────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────────

def admin_dashboard(request):
    now = timezone.now()
    last_30_days = now - timedelta(days=30)

    logs = VisitorLog.objects.filter(visited_at__gte=last_30_days)
    page_views      = logs.count()
    unique_visitors = logs.values("ip_address").distinct().count()
    bounce_ips      = logs.values("ip_address").annotate(count=Count("id")).filter(count=1).count()
    bounce_rate     = (bounce_ips / unique_visitors * 100) if unique_visitors else 0

    total_suppliers  = Supplier.objects.count()
    active_suppliers = Supplier.objects.filter(is_active=True).count()
    avg_supplier_score = SupplierPerformanceScore.objects.aggregate(avg=Avg("final_score"))["avg"] or 0
    high_risk_suppliers = SupplierPerformanceScore.objects.filter(risk_index__gt=70).count()

    total_deliveries = Delivery.objects.count()
    on_time_rate  = (Delivery.objects.filter(delivery_status="ON_TIME").count() / total_deliveries * 100) if total_deliveries else 0
    damaged_rate  = (Delivery.objects.filter(condition_status="DAMAGED").count() / total_deliveries * 100) if total_deliveries else 0

    total_complaints    = Complaint.objects.count()
    unresolved_complaints = Complaint.objects.filter(resolved=False).count()

    total_skus = InventoryItem.objects.count()
    low_stock  = InventoryItem.objects.filter(quantity_in_stock__lte=F("reorder_level")).count()
    inventory_value = InventoryItem.objects.aggregate(
        total=Sum(ExpressionWrapper(F("quantity_in_stock") * F("unit_cost"), output_field=FloatField()))
    )["total"] or 0

    total_customers = Customer.objects.count()
    avg_ltv   = Customer.objects.aggregate(avg=Avg("lifetime_value"))["avg"] or 0
    avg_churn = Customer.objects.aggregate(avg=Avg("churn_probability"))["avg"] or 0

    total_reviews      = Review.objects.count()
    avg_review_score   = Review.objects.aggregate(avg=Avg("overall_weighted_score"))["avg"] or 0
    positive_sentiment = SentimentAnalysis.objects.filter(sentiment_label="Positive").count()
    total_sentiments   = SentimentAnalysis.objects.count()
    sentiment_positive_rate = (positive_sentiment / total_sentiments * 100) if total_sentiments else 0

    avg_market_growth = MarketTrend.objects.aggregate(avg=Avg("overall_growth_rate"))["avg"] or 0
    avg_market_risk   = MarketTrend.objects.aggregate(avg=Avg("risk_level"))["avg"] or 0

    context = {
        "bounce_rate": round(bounce_rate, 2), "page_views": page_views, "unique_visitors": unique_visitors,
        "total_suppliers": total_suppliers, "active_suppliers": active_suppliers,
        "avg_supplier_score": round(avg_supplier_score, 2), "high_risk_suppliers": high_risk_suppliers,
        "on_time_rate": round(on_time_rate, 2), "damaged_rate": round(damaged_rate, 2),
        "total_complaints": total_complaints, "unresolved_complaints": unresolved_complaints,
        "total_skus": total_skus, "low_stock": low_stock, "inventory_value": round(inventory_value, 2),
        "total_customers": total_customers, "avg_ltv": round(float(avg_ltv), 2), "avg_churn": round(avg_churn, 2),
        "total_reviews": total_reviews, "avg_review_score": round(avg_review_score, 2),
        "sentiment_positive_rate": round(sentiment_positive_rate, 2),
        "avg_market_growth": round(avg_market_growth, 2), "avg_market_risk": round(avg_market_risk, 2),
    }
    return render(request, "dashboard.html", context)


# ─────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────

def dashboard(request):
    context = {}

    context["total_visits"]    = VisitorLog.objects.count()
    context["unique_visitors"] = VisitorLog.objects.values("ip_address").distinct().count()
    context["top_pages"]       = VisitorLog.objects.values("path").annotate(visits=Count("id")).order_by("-visits")[:10]
    context["top_locations"]   = VisitorLog.objects.values("location").annotate(count=Count("id")).order_by("-count")[:5]

    context["total_suppliers"]   = Supplier.objects.count()
    context["active_suppliers"]  = Supplier.objects.filter(is_active=True).count()
    context["inactive_suppliers"] = Supplier.objects.filter(is_active=False).count()
    context["suppliers"]         = Supplier.objects.all()

    scores = SupplierPerformanceScore.objects.select_related("supplier")
    context["supplier_scores"]    = scores
    context["avg_supplier_score"] = scores.aggregate(avg=Avg("final_score"))["avg"]
    context["excellent_suppliers"] = scores.filter(rating_category="Excellent").count()
    context["good_suppliers"]      = scores.filter(rating_category="Good").count()
    context["average_suppliers"]   = scores.filter(rating_category="Average").count()
    context["poor_suppliers"]      = scores.filter(rating_category="Poor").count()

    sentiment_counts = SupplierSentiment.objects.values("sentiment_label").annotate(count=Count("id"))
    positive = neutral = negative = 0
    for s in sentiment_counts:
        if s["sentiment_label"] == "Positive":   positive = s["count"]
        elif s["sentiment_label"] == "Neutral":  neutral  = s["count"]
        elif s["sentiment_label"] == "Negative": negative = s["count"]
    context["positive_sentiments"] = positive
    context["neutral_sentiments"]  = neutral
    context["negative_sentiments"] = negative
    context["sentiments"] = SupplierSentiment.objects.select_related("supplier")[:100]

    context["total_customers"]    = Customer.objects.count()
    context["avg_lifetime_value"] = Customer.objects.aggregate(avg=Avg("lifetime_value"))["avg"]
    context["avg_churn"]          = Customer.objects.aggregate(avg=Avg("churn_probability"))["avg"]
    context["avg_engagement"]     = Customer.objects.aggregate(avg=Avg("engagement_score"))["avg"]

    low    = Customer.objects.filter(churn_probability__lt=0.3).count()
    medium = Customer.objects.filter(churn_probability__gte=0.3, churn_probability__lt=0.7).count()
    high   = Customer.objects.filter(churn_probability__gte=0.7).count()
    context["churn_labels"] = json.dumps(["Low Risk", "Medium Risk", "High Risk"])
    context["churn_values"] = json.dumps([low, medium, high])

    context["total_profiles"]     = CustomerProfile.objects.count()
    context["profiles_by_location"] = CustomerProfile.objects.values("location").annotate(count=Count("id")).order_by("-count")[:10]

    context["total_brands"] = FastFoodBrand.objects.count()
    context["brands"]       = FastFoodBrand.objects.all()

    context["total_reviews"]   = Review.objects.count()
    context["avg_review_score"] = Review.objects.aggregate(avg=Avg("overall_weighted_score"))["avg"]
    context["reviews"]         = Review.objects.select_related("brand", "customer")[:100]

    engagement = EngagementMetric.objects.select_related("customer")
    context["engagement_records"]  = engagement.count()
    context["total_page_views"]    = engagement.aggregate(total=Sum("page_views"))["total"]
    context["total_clicks"]        = engagement.aggregate(total=Sum("clicks"))["total"]
    context["avg_loyalty_index"]   = engagement.aggregate(avg=Avg("loyalty_index"))["avg"]

    events = [{"title": f"{e.customer.full_name} Engagement", "start": e.recorded_month.strftime("%Y-%m-%d")} for e in engagement]
    context["calendar_events"] = json.dumps(events)

    inventory = InventoryItem.objects.all()
    context["inventory_items"]  = inventory
    context["inventory_count"]  = inventory.count()
    context["low_stock_items"]  = inventory.filter(quantity_in_stock__lte=5).count()
    inv_by_cat = inventory.values("category").annotate(count=Count("id"))
    context["inventory_chart_labels"] = json.dumps([i["category"] for i in inv_by_cat])
    context["inventory_chart_values"] = json.dumps([i["count"] for i in inv_by_cat])

    deliveries = Delivery.objects.select_related("supplier")
    context["deliveries"]       = deliveries
    context["total_deliveries"] = deliveries.count()
    delivery_chart = deliveries.values("delivery_status").annotate(count=Count("id"))
    context["delivery_labels"] = json.dumps([d["delivery_status"] for d in delivery_chart])
    context["delivery_values"] = json.dumps([d["count"] for d in delivery_chart])

    complaints = Complaint.objects.select_related("supplier")
    context["complaints"]       = complaints
    context["total_complaints"] = complaints.count()

    trends = MarketTrend.objects.all()
    context["trends"]        = trends
    context["market_trends"] = trends.count()
    trend_chart = MarketTrend.objects.values("trend_title").annotate(count=Count("id"))
    context["trend_labels"] = json.dumps([t["trend_title"] for t in trend_chart])
    context["trend_values"] = json.dumps([t["count"] for t in trend_chart])

    indicators = MarketIndicator.objects.all()
    context["market_indicators"] = indicators
    context["indicator_count"]   = indicators.count()
    ind_chart = MarketIndicator.objects.values("indicator_name").annotate(count=Count("id"))
    context["indicator_labels"] = json.dumps([i["indicator_name"] for i in ind_chart])
    context["indicator_values"] = json.dumps([i["count"] for i in ind_chart])

    competitors = CompetitorMarketData.objects.all()
    context["competitors"]      = competitors
    context["competitor_count"] = competitors.count()

    decisions = DecisionRecommendation.objects.all()
    context["decision_reports"] = decisions
    context["decision_count"]   = decisions.count()

    return render(request, "index.html", context)


def home_view(request):
    return render(request, "home.html")


# ─────────────────────────────────────────────
# SUPPLIER DASHBOARD  (FIX: was crashing when no data)
# ─────────────────────────────────────────────

def supplierdashboard(request):
    total_suppliers  = Supplier.objects.count()
    total_deliveries = Delivery.objects.count()
    total_complaints = Complaint.objects.count()

    avg_score_data = SupplierPerformanceScore.objects.aggregate(Avg("final_score"))
    avg_score = round(avg_score_data["final_score__avg"] or 0, 2)

    supplier_scores = SupplierPerformanceScore.objects.select_related("supplier").order_by("-final_score")

    # FIX: safe fallback when no scores exist
    best_supplier   = supplier_scores.first().supplier.name if supplier_scores.exists() else "N/A"
    risky_qs        = SupplierPerformanceScore.objects.order_by("-risk_index").first()
    risky_supplier  = risky_qs.supplier.name if risky_qs else "N/A"

    complaint_supplier_data = (
        Complaint.objects.values("supplier__name")
        .annotate(c=Count("id"))
        .order_by("-c")
        .first()
    )
    complaint_supplier = complaint_supplier_data["supplier__name"] if complaint_supplier_data else "N/A"

    context = {
        "total_suppliers":  total_suppliers,
        "avg_score":        avg_score,
        "total_deliveries": total_deliveries,
        "total_complaints": total_complaints,
        "supplier_scores":  supplier_scores,
        "best_supplier":    best_supplier,
        "risky_supplier":   risky_supplier,
        # FIX: pass ALL suppliers so new ones appear in the list
        "suppliers":        Supplier.objects.all().order_by("name"),
        "deliveries":       Delivery.objects.all(),
        "reviews":          SupplierReview.objects.all(),
        "complaints":       Complaint.objects.all(),
        "complaint_supplier": complaint_supplier,
    }
    return render(request, "supplierdashboard.html", context)


# ─────────────────────────────────────────────
# CUSTOMER DASHBOARD
# ─────────────────────────────────────────────

def customerdashboard(request):
    reviews    = Review.objects.select_related("customer", "brand")
    sentiments = SentimentAnalysis.objects.select_related("review__customer", "review__brand")
    customers  = CustomerProfile.objects.all()

    highest_positive = sentiments.aggregate(Max("final_sentiment_score"))["final_sentiment_score__max"]
    highest_negative = sentiments.aggregate(Min("final_sentiment_score"))["final_sentiment_score__min"]

    positive = sentiments.filter(final_sentiment_score__gt=0).count()
    negative = sentiments.filter(final_sentiment_score__lt=0).count()
    neutral  = sentiments.filter(final_sentiment_score=0).count()

    review_trend  = reviews.annotate(date=TruncDate("created_at")).values("date").annotate(count=Count("id")).order_by("date")
    trend_dates   = [str(r["date"]) for r in review_trend]
    trend_counts  = [r["count"] for r in review_trend]

    context = {
        "reviews": reviews, "sentiments": sentiments, "customers": customers,
        "total_entries": reviews.count(), "total_customers": customers.count(),
        "highest_positive": highest_positive, "highest_negative": highest_negative,
        "positive": positive, "neutral": neutral, "negative": negative,
        "trend_dates": trend_dates, "trend_counts": trend_counts,
    }
    return render(request, "customerdashboard.html", context)


# ─────────────────────────────────────────────
# INVENTORY
# ─────────────────────────────────────────────

def inventory(request):
    inventory  = InventoryItem.objects.select_related("supplier")
    deliveries = Delivery.objects.select_related("supplier")

    inventory_value = inventory.aggregate(
        total=Sum(ExpressionWrapper(F("quantity_in_stock") * F("unit_cost"), output_field=DecimalField()))
    )["total"] or 0

    top_suppliers = deliveries.values("supplier__name").annotate(deliveries_count=Count("id")).order_by("-deliveries_count")[:5]

    context = {
        "inventory": inventory, "deliveries": deliveries,
        "total_products":    inventory.count(),
        "total_stock":       inventory.aggregate(Sum("quantity_in_stock"))["quantity_in_stock__sum"] or 0,
        "low_stock_items":   inventory.filter(quantity_in_stock__lte=F("reorder_level")).count(),
        "active_products":   inventory.filter(is_active=True).count(),
        "inactive_products": inventory.filter(is_active=False).count(),
        "inventory_value":   inventory_value,
        "avg_selling_price": inventory.aggregate(Avg("selling_price"))["selling_price__avg"] or 0,
        "total_deliveries":      deliveries.count(),
        "on_time_deliveries":    deliveries.filter(delivery_status="ON_TIME").count(),
        "late_deliveries":       deliveries.filter(delivery_status="LATE").count(),
        "early_deliveries":      deliveries.filter(delivery_status="EARLY").count(),
        "damaged_goods":         deliveries.filter(condition_status="DAMAGED").count(),
        "partial_deliveries":    deliveries.filter(condition_status="PARTIAL").count(),
        "documentation_issues":  deliveries.filter(documentation_complete=False).count(),
        "top_suppliers": top_suppliers,
    }
    return render(request, "inventory.html", context)


def audit(request):
    engagement = EngagementMetric.objects.all()
    visitors   = VisitorLog.objects.all()
    context = {
        "engagement_metrics": engagement, "visitor_logs": visitors,
        "total_visitors":    visitors.count(),
        "total_page_views":  engagement.aggregate(Sum("page_views"))["page_views__sum"] or 0,
        "total_clicks":      engagement.aggregate(Sum("clicks"))["clicks__sum"] or 0,
        "total_messages":    engagement.aggregate(Sum("messages_sent"))["messages_sent__sum"] or 0,
    }
    return render(request, "audit.html", context)


# ─────────────────────────────────────────────
# CUSTOMER REVIEW  (FIX: gender choices in template)
# ─────────────────────────────────────────────

def customer_review_view(request):
    if "page_views" not in request.session:
        request.session["page_views"] = 0
    request.session["page_views"] += 1

    if "start_time" not in request.session:
        request.session["start_time"] = str(timezone.now())

    if request.method == "POST":
        try:
            start_time  = timezone.datetime.fromisoformat(request.session["start_time"])
            time_spent  = (timezone.now() - start_time).total_seconds()
            clicks      = 1

            customer = CustomerProfile.objects.create(
                full_name        = request.POST.get("full_name"),
                age_range        = request.POST.get("age_range"),
                gender           = request.POST.get("gender"),
                location         = request.POST.get("location"),
                employment_status   = request.POST.get("employment_status"),
                eating_out_frequency = request.POST.get("eating_out_frequency"),
                preferred_brand  = request.POST.get("preferred_brand"),
            )

            brand, _ = FastFoodBrand.objects.get_or_create(
                name=request.POST.get("restaurant_name"),
                branch=request.POST.get("branch"),
            )

            review = Review.objects.create(
                customer=customer, brand=brand,
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
                improvement_suggestions=request.POST.get("improvement_suggestions"),
            )

            vader_score, bert_score = analyze_sentiment(review.full_experience or "")
            final_sentiment = (vader_score + bert_score) / 2
            sentiment_label = "Positive" if final_sentiment >= 0 else "Negative"

            SentimentAnalysis.objects.create(
                review=review,
                vader_score=vader_score, bert_score=bert_score,
                final_sentiment_score=final_sentiment, sentiment_label=sentiment_label,
            )

            page_views = request.session.get("page_views", 1)
            engagement_score = (page_views * 0.2) + (clicks * 0.3) + (time_spent * 0.001)
            loyalty_index    = (review.nps_score * 0.6) + (engagement_score * 0.4)

            EngagementMetric.objects.create(
                customer=customer, review=review,
                page_views=page_views, clicks=clicks,
                messages_sent=0, support_tickets=0,
                engagement_score=engagement_score, loyalty_index=loyalty_index,
            )

            # ── EMAIL NOTIFICATION ──────────────────────────────────────
            admin_email = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", settings.DEFAULT_FROM_EMAIL)
            send_html_email(
                subject=f"New Customer Review — {brand.name}",
                template_name="customeremail.html",
                context={
                    "review":    review,
                    "customer":  customer,
                    "brand":     brand,
                    "sentiment": sentiment_label,
                    "score":     round(final_sentiment, 3),
                    "timestamp": timezone.now(),
                },
                recipient_list=[admin_email],
            )

            request.session.flush()
            messages.success(request, "Thank you! Your review has been submitted successfully.")
            return redirect("customer")

        except Exception as e:
            messages.error(request, f"An error occurred while submitting your review: {str(e)}")

    return render(request, "customer.html")


# ─────────────────────────────────────────────
# SUPPLIER REGISTRATION
# ─────────────────────────────────────────────

def supplier_register(request):
    print("allons")
    if request.method == "POST":
        name          = request.POST.get("name")
        print(name)
        company_name  = request.POST.get("company_name")
        supplier_code = request.POST.get("supplier_code")
        contact_person = request.POST.get("contact_person")
        phone         = request.POST.get("phone")
        email         = request.POST.get("email")
        location      = request.POST.get("location")
        is_active     = request.POST.get("is_active") == "on"
        
        print(supplier_code)
        if not name or not supplier_code:
            messages.error(request, "Name and Supplier Code are required!")
            return redirect("register")

        supplier = Supplier.objects.create(
            name=name, company_name=company_name,
            supplier_code=supplier_code, contact_person=contact_person,
            phone=phone, email=email, location=location,
            is_active=is_active, created_at=timezone.now(),
        )
        print(supplier)

        # ── EMAIL NOTIFICATION ──────────────────────────────────────
        admin_email = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", settings.DEFAULT_FROM_EMAIL)
        recipients  = [admin_email]
        if supplier.email:
            recipients.append(supplier.email)

        send_html_email(
            subject=f"New Supplier Registered — {supplier.name}",
            template_name="email.html",
            context={"supplier": supplier, "timestamp": timezone.now()},
            recipient_list=recipients,
        )

        messages.success(request, f"Supplier {name} registered successfully!")
        return redirect("register")

    return render(request, "supplierregistration.html", {"page_title": "Supplier Registration"})


# ─────────────────────────────────────────────
# DELIVERY  (FIX: lookup by order_number to auto-fill)
# ─────────────────────────────────────────────

def delivery_lookup(request):
    """AJAX endpoint — returns delivery JSON by order_number."""
    order_number = request.GET.get("order_number", "").strip()
    if not order_number:
        return JsonResponse({"found": False})
    try:
        d = Delivery.objects.select_related("supplier").get(order_number=order_number)
        return JsonResponse({
            "found":             True,
            "supplier_id":       d.supplier.id,
            "supplier_name":     d.supplier.name,
            "invoice_number":    d.invoice_number,
            "product_category":  d.product_category,
            "quantity_ordered":  d.quantity_ordered,
            "expected_date":     str(d.expected_delivery_date),
        })
    except Delivery.DoesNotExist:
        return JsonResponse({"found": False})


def record_delivery(request):
    suppliers = Supplier.objects.filter(is_active=True)

    if request.method == "POST":
        supplier_id        = request.POST.get("supplier")
        order_number       = request.POST.get("order_number")
        invoice_number     = request.POST.get("invoice_number")
        product_category   = request.POST.get("product_category")
        product_name       = request.POST.get("product_name")
        sku                = request.POST.get("sku")
        quantity_ordered   = float(request.POST.get("quantity_ordered") or 0)
        quantity_delivered = float(request.POST.get("quantity_delivered") or 0)
        delivery_status    = request.POST.get("delivery_status")
        condition_status   = request.POST.get("condition_status")
        vehicle_registration = request.POST.get("vehicle_registration")
        driver_name        = request.POST.get("driver_name")
        expected_delivery_date = request.POST.get("expected_delivery_date")
        actual_delivery_date   = request.POST.get("actual_delivery_date")
        delivery_comment   = request.POST.get("delivery_comment", "")

        supplier = Supplier.objects.get(id=supplier_id)

        delivery = Delivery.objects.create(
            supplier=supplier,
            order_number=order_number, invoice_number=invoice_number,
            product_category=product_category,
            quantity_ordered=quantity_ordered, quantity_delivered=quantity_delivered,
            delivery_status=delivery_status, condition_status=condition_status,
            vehicle_registration=vehicle_registration, driver_name=driver_name,
            expected_delivery_date=expected_delivery_date,
            actual_delivery_date=actual_delivery_date,
            created_at=timezone.now(),
        )

        if sku and product_name:
            item, created = InventoryItem.objects.get_or_create(
                supplier=supplier, sku=sku,
                defaults={
                    "name": product_name, "category": product_category,
                    "quantity_in_stock": quantity_delivered, "unit_cost": 0,
                    "selling_price": 0, "warehouse_location": "Default Warehouse",
                    "last_restocked": timezone.now(),
                },
            )
            if not created:
                item.quantity_in_stock += quantity_delivered
                item.last_restocked = timezone.now()
                item.save()

        if delivery_comment:
            vader, bert = analyze_sentiment(delivery_comment)
            SupplierSentiment.objects.create(
                supplier=supplier, source_type="delivery", source_id=delivery.id,
                text=delivery_comment, sentiment_label=vader, confidence_score=vader,
            )

        SupplierPerformanceScore.objects.get_or_create(supplier=supplier)
        messages.success(request, f"Delivery for {supplier.name} recorded successfully!")
        return redirect("delivery")

    return render(request, "delivery_form.html", {
        "suppliers":   suppliers,
        "page_title":  "Record Supplier Delivery",
    })


# ─────────────────────────────────────────────
# SUPPLIER REVIEW  (FIX: redirect name was wrong)
# ─────────────────────────────────────────────

def supplier_review(request):
    suppliers = Supplier.objects.filter(is_active=True)

    if request.method == "POST":
        supplier_id         = request.POST.get("supplier")
        communication_score = float(request.POST.get("communication_score") or 0)
        flexibility_score   = float(request.POST.get("flexibility_score") or 0)
        documentation_score = float(request.POST.get("documentation_score") or 0)
        pricing_score       = float(request.POST.get("pricing_score") or 0)
        review_comment      = request.POST.get("review_comment", "")

        supplier = Supplier.objects.get(id=supplier_id)

        review = SupplierReview.objects.create(
            supplier=supplier,
            communication_score=communication_score,
            flexibility_score=flexibility_score,
            documentation_score=documentation_score,
            price_competitiveness_score=pricing_score,
            review_comment=review_comment,
            created_at=timezone.now(),
        )

        if review_comment:
            vader, bert = analyze_sentiment(review_comment)
            SupplierSentiment.objects.create(
                supplier=supplier, source_type="review", source_id=review.id,
                text=review_comment, sentiment_label=vader, confidence_score=vader,
            )

        SupplierPerformanceScore.objects.get_or_create(supplier=supplier)

        # ── EMAIL NOTIFICATION ──────────────────────────────────────
        admin_email = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", settings.DEFAULT_FROM_EMAIL)
        recipients  = [admin_email]
        if supplier.email:
            recipients.append(supplier.email)

        send_html_email(
            subject=f"Supplier Review Submitted — {supplier.name}",
            template_name="supplieremail.html",
            context={
                "supplier":       supplier,
                "review":         review,
                "review_comment": review_comment,
                "timestamp":      timezone.now(),
                # pass as list of (label, value) tuples for easy template rendering
                "scores": [
                    ("Communication",        communication_score),
                    ("Flexibility",          flexibility_score),
                    ("Documentation",        documentation_score),
                    ("Price Competitiveness", pricing_score),
                ],
            },
            recipient_list=recipients,
        )

        messages.success(request, f"Review for {supplier.name} recorded successfully!")
        # FIX: correct URL name
        return redirect("review")

    return render(request, "supplier_review.html", {
        "suppliers":  suppliers,
        "page_title": "Supplier Review",
    })


# ─────────────────────────────────────────────
# COMPLAINT LOGGING  (FIX: redirect name was wrong)
# ─────────────────────────────────────────────

def record_complaint(request):
    suppliers = Supplier.objects.filter(is_active=True)

    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        description = request.POST.get("description", "")
        supplier    = Supplier.objects.get(id=supplier_id)

        complaint = Complaint.objects.create(
            supplier=supplier, description=description,
            created_at=timezone.now(),
        )

        if description:
            vader, bert = analyze_sentiment(description)
            final_score = min(vader, 0)   # ensure negative for complaints
            SupplierSentiment.objects.create(
                supplier=supplier, source_type="complaint", source_id=complaint.id,
                text=description, sentiment_label=vader, confidence_score=final_score,
            )

        SupplierPerformanceScore.objects.get_or_create(supplier=supplier)

        # ── EMAIL NOTIFICATION ──────────────────────────────────────
        admin_email = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", settings.DEFAULT_FROM_EMAIL)
        recipients  = [admin_email]
        if supplier.email:
            recipients.append(supplier.email)

        send_html_email(
            subject=f"⚠️ Supplier Complaint Filed — {supplier.name}",
            template_name="complaintemail.html",
            context={
                "supplier":    supplier,
                "complaint":   complaint,
                "description": description,
                "timestamp":   timezone.now(),
            },
            recipient_list=recipients,
        )

        messages.success(request, f"Complaint for {supplier.name} recorded successfully!")
        # FIX: correct URL name
        return redirect("complaint")

    return render(request, "complaint_form.html", {
        "suppliers":  suppliers,
        "page_title": "Record Supplier Complaint",
    })


# ─────────────────────────────────────────────
# OTHER VIEWS
# ─────────────────────────────────────────────

def supplier_reviews(request, supplier_id):
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    reviews  = Review.objects.filter(supplier=supplier)
    return render(request, "supplier_reviews.html", {"supplier": supplier, "reviews": reviews})

def customer_reviews(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    reviews  = Review.objects.filter(customer=customer)
    return render(request, "customer_reviews.html", {"customer": customer, "reviews": reviews})

def supplier_management(request):
    suppliers = Supplier.objects.all().order_by("name")
    return render(request, "supplier_manage.html", {"suppliers": suppliers})

def supplier_sentiments(request, supplier_id):
    supplier   = get_object_or_404(Supplier, pk=supplier_id)
    sentiments = SentimentAnalysis.objects.filter(supplier=supplier)
    return render(request, "supplier_sentiments.html", {"supplier": supplier, "sentiments": sentiments})

def customer_sentiments(request, customer_id):
    customer   = get_object_or_404(Customer, pk=customer_id)
    sentiments = SentimentAnalysis.objects.filter(customer=customer)
    return render(request, "customer_sentiments.html", {"customer": customer, "sentiments": sentiments})

def customer_engagement(request):
    return render(request, "customer_engagement.html", {"engagement_data": EngagementMetric.objects.all()})

def store_inventory(request):
    return render(request, "store_inventory.html", {"inventory": InventoryItem.objects.all()})

def performance_benchmark(request):
    benchmarks = Benchmark.objects.order_by("-benchmark_score")
    return render(request, "benchmark.html", {"benchmarks": benchmarks})

def market_industry_trends(request):
    trends = MarketTrend.objects.order_by("-created_at")
    return render(request, "market_trends.html", {"trends": trends})


# ─────────────────────────────────────────────
# AI / REPORTS
# ─────────────────────────────────────────────

def extract_json(text):
    try:
        text = re.sub(r"^```json\s*", "", text.strip())
        text = re.sub(r"^```", "", text)
        text = re.sub(r"```$", "", text)
        return json.loads(text)
    except Exception:
        return None


def call_openrouter(system_prompt: str, user_prompt: str, max_tokens: int = 900) -> str:
    if not OPENROUTER_API_KEY:
        return ""
    try:
        resp = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type":  "application/json",
                "HTTP-Referer":  "https://kpifastfood.app",
                "X-Title":       "KPI Fastfood Analytics",
            },
            json={
                "model": OPENROUTER_MODEL, "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error("OPENROUTER ERROR: %s", e)
        return ""


def build_data_snapshot() -> dict:
    perf_scores   = SupplierPerformanceScore.objects.select_related("supplier")
    total_deliveries = Delivery.objects.count()
    on_time_count    = Delivery.objects.filter(delivery_status="ON_TIME").count()

    return {
        "supplier_total":    Supplier.objects.filter(is_active=True).count(),
        "avg_final_score":   round(perf_scores.aggregate(a=Avg("final_score"))["a"] or 0, 1),
        "avg_risk_index":    round(perf_scores.aggregate(a=Avg("risk_index"))["a"] or 0, 1),
        "avg_trust_index":   round(perf_scores.aggregate(a=Avg("trust_index"))["a"] or 0, 1),
        "high_risk_suppliers": perf_scores.filter(risk_index__gte=70).count(),
        "rating_distribution": {cat: perf_scores.filter(rating_category=cat).count() for cat in ("Excellent", "Good", "Average", "Poor")},
        "total_deliveries":  total_deliveries,
        "on_time_rate":      round((on_time_count / total_deliveries * 100) if total_deliveries else 0, 1),
        "late_deliveries":   Delivery.objects.filter(delivery_status="LATE").count(),
        "damaged_deliveries": Delivery.objects.filter(condition_status="DAMAGED").count(),
        "total_complaints":  Complaint.objects.count(),
        "unresolved_complaints": Complaint.objects.filter(resolved=False).count(),
        "high_severity_complaints": Complaint.objects.filter(severity_level__gte=4).count(),
        "customer_review_count": Review.objects.count(),
        "avg_weighted_customer_score": round(Review.objects.aggregate(a=Avg("overall_weighted_score"))["a"] or 0, 1),
        "avg_nps": round(Review.objects.aggregate(a=Avg("nps_score"))["a"] or 0, 1),
        "low_stock_items": InventoryItem.objects.filter(quantity_in_stock__lte=F("reorder_level"), is_active=True).count(),
        "top_suppliers_by_reviews": list(Supplier.objects.annotate(rc=Count("reviews")).order_by("-rc")[:5].values("name", "rc")),
    }


def get_ai_insights(snapshot: dict) -> dict:
    SYSTEM = (
        "You are an expert supply-chain and restaurant operations analyst.\n"
        "Return ONLY valid JSON. No markdown, no explanations, no code blocks.\n\n"
        'Format EXACTLY: {"summary":"text","risks":["...","..."],"opportunities":["...","..."],"actions":["...","...","..."]}'
    )
    USER = f"Here is today's KPI snapshot:\n{json.dumps(snapshot, indent=2)}\n\nProvide a concise strategic analysis."
    raw  = call_openrouter(SYSTEM, USER, max_tokens=700)

    if not raw:
        return {"summary": "", "risks": [], "opportunities": [], "actions": []}
    try:
        text = re.sub(r"^```json\s*|^```|```$", "", raw.strip())
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON found")
        parsed = json.loads(match.group(0))
        return {k: parsed.get(k, [] if k != "summary" else "") for k in ("summary", "risks", "opportunities", "actions")}
    except Exception as e:
        logger.error("AI parse error: %s", e)
        return {"summary": "AI response could not be structured properly.", "risks": [], "opportunities": [], "actions": []}


def report_and_recommendations(request):
    snapshot = build_data_snapshot()
    ai       = get_ai_insights(snapshot)

    top_performers  = Supplier.objects.annotate(review_count=Count("reviews")).order_by("-review_count")[:5]
    decision_reports = DecisionRecommendation.objects.order_by("-created_at")[:12]

    context = {
        "avg_supplier_rating": round(Review.objects.aggregate(avg=Avg("overall_weighted_score"))["avg"] or 0, 1),
        "top_performers":      top_performers,
        "decision_count":      decision_reports.count(),
        "decision_reports":    decision_reports,
        "snapshot":            snapshot,
        "ai_summary":          ai.get("summary", ""),
        "ai_risks":            ai.get("risks", []),
        "ai_opportunities":    ai.get("opportunities", []),
        "ai_actions":          ai.get("actions", []),
        "ai_available":        bool(OPENROUTER_API_KEY),
        "generated_at":        timezone.now(),
    }
    return render(request, "reports.html", context)


# ─────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS    = 300


def _get_login_cache_key(identifier: str, ip: str) -> str:
    return f"login_attempts:{identifier or 'anonymous'}:{ip or 'unknown_ip'}"


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("dashboard")

    ip = request.META.get("REMOTE_ADDR", "")

    if request.method == "POST":
        identifier = (request.POST.get("identifier") or "").strip()
        password   =  request.POST.get("password") or ""

        cache_key    = _get_login_cache_key(identifier, ip)
        attempts_info = cache.get(cache_key, {"count": 0, "locked_until": None})

        locked_until = attempts_info.get("locked_until")
        now = timezone.now()
        if locked_until and now < locked_until:
            remaining = int((locked_until - now).total_seconds())
            messages.error(request, f"Too many failed attempts. Try again in {remaining} seconds.")
            return render(request, "login.html", status=403)

        user = authenticate(request, username=identifier, password=password)
        if user is None:
            try:
                email_user = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=email_user.get_username(), password=password)
            except User.DoesNotExist:
                user = None

        if user is not None and user.is_active:
            cache.delete(cache_key)
            auth_login(request, user)
            messages.success(request, "Login successful.")
            next_url = request.POST.get("next") or request.GET.get("next") or getattr(settings, "LOGIN_REDIRECT_URL", "dashboard")
            return redirect(next_url)

        attempts     = attempts_info.get("count", 0) + 1
        lockout_until = None
        if attempts >= MAX_LOGIN_ATTEMPTS:
            lockout_until = timezone.now() + timezone.timedelta(seconds=LOCKOUT_SECONDS)
            messages.error(request, "Too many failed attempts. Your account is temporarily locked.")
        else:
            messages.error(request, "Invalid credentials. Please try again.")

        cache.set(cache_key, {"count": attempts, "locked_until": lockout_until}, timeout=LOCKOUT_SECONDS)

    return render(request, "login.html")


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# ─────────────────────────────────────────────
# RBAC
# ─────────────────────────────────────────────

def role_required(roles: Optional[Iterable[str]] = None, groups: Optional[Iterable[str]] = None, redirect_field_name: str = "next") -> Callable:
    if roles  is not None: roles  = set(roles)
    if groups is not None: groups = set(groups)

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def _wrapped_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path(), "login", redirect_field_name)

            user = request.user
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            if roles and getattr(user, "role", None) in roles:
                return view_func(request, *args, **kwargs)
            if groups and set(user.groups.values_list("name", flat=True)).intersection(groups):
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("You do not have permission to access this resource.")
        return _wrapped_view
    return decorator


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")

def admin_dashboard_view(request: HttpRequest) -> HttpResponse:
    return render(request, "admin_dashboard.html")

def insights_view(request: HttpRequest) -> HttpResponse:
    return render(request, "insights.html")

def inventory_view(request: HttpRequest) -> HttpResponse:
    return render(request, "inventory.html")