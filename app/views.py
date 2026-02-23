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
        # Save Review (same as before)
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
        # SENTIMENT
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

        return redirect("thank_you")

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
def report_and_recommendations(request):
    # Summaries from models
    avg_supplier_rating = Review.objects.aggregate(Avg("rating"))
    top_performers = Supplier.objects.annotate(review_count=Count("review")).order_by("-review_count")[:5]

    context = {
        "avg_supplier_rating": avg_supplier_rating,
        "top_performers": top_performers
    }
    return render(request, "reports.html", context)

# Performance benchmark page
def performance_benchmark(request):
    benchmarks = Benchmark.objects.order_by("-score")
    return render(request, "performance_benchmark.html", {"benchmarks": benchmarks})

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
            comment=delivery_comment,
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
            vader, bert, final_score = analyze_sentiment(delivery_comment)
            SupplierSentiment.objects.create(
                supplier=supplier,
                source_type="delivery",
                source_id=delivery.id,
                text=delivery_comment,
                vader_score=vader,
                bert_score=bert,
                final_sentiment_score=final_score
            )

        # Update supplier performance
        perf, _ = SupplierPerformanceScore.objects.get_or_create(supplier=supplier)
        perf.update_from_delivery(delivery)
        perf.update_from_sentiments()

        messages.success(request, f"Delivery for {supplier.name} recorded successfully!")
        return redirect("supplier:delivery")

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
            pricing_score=pricing_score,
            comment=review_comment,
            created_at=timezone.now()
        )

        # Analyze review sentiment
        if review_comment:
            vader, bert, final_score = analyze_sentiment(review_comment)
            SupplierSentiment.objects.create(
                supplier=supplier,
                source_type="review",
                source_id=review.id,
                text=review_comment,
                vader_score=vader,
                bert_score=bert,
                final_sentiment_score=final_score
            )

        # Update supplier performance
        perf, _ = SupplierPerformanceScore.objects.get_or_create(supplier=supplier)
        perf.update_from_review(review)
        perf.update_from_sentiments()
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
            vader, bert, final_score = analyze_sentiment(description)
            final_score = min(final_score, 0)  # ensure negative
            SupplierSentiment.objects.create(
                supplier=supplier,
                source_type="complaint",
                source_id=complaint.id,
                text=description,
                vader_score=vader,
                bert_score=bert,
                final_sentiment_score=final_score
            )

        # Update supplier performance
        perf, _ = SupplierPerformanceScore.objects.get_or_create(supplier=supplier)
        perf.update_from_complaint(complaint)
        perf.update_from_sentiments()
        messages.success(request, f"Complaint for {supplier.name} recorded successfully!")
        return redirect("record_complaint")

    return render(request, "complaint_form.html", {
        "suppliers": suppliers,
        "page_title": "Record Supplier Complaint"
    })