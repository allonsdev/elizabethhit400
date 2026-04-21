from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────
    path('',          views.home_view,   name='home'),
    path('login/',    views.login_view,  name='login'),
    path('logout/',   views.logout_view, name='logout'),

    # ── Dashboards ────────────────────────────────────────────────────
    path('dashboard/',          views.dashboard,          name='dashboard'),
    path('admin/dashboard/',    views.admin_dashboard_view, name='admin_dashboard'),
    path('supplierdashboard/',  views.supplierdashboard,  name='supplierdashboard'),
    path('customerdashboard/',  views.customerdashboard,  name='customerdashboard'),

    # ── Supplier flows ────────────────────────────────────────────────
    path('register/',    views.supplier_register, name='register'),
    path('delivery/',    views.record_delivery,   name='delivery'),
    path('review/',      views.supplier_review,   name='review'),
    path('complaint/',   views.record_complaint,  name='complaint'),

    # AJAX lookup for delivery auto-fill
    path('delivery/lookup/', views.delivery_lookup, name='delivery_lookup'),

    path('suppliers/manage/', views.supplier_management, name='supplier_manage'),
    path('supplier/<int:supplier_id>/sentiments/', views.supplier_sentiments, name='supplier_sentiments'),

    # ── Customer flows ────────────────────────────────────────────────
    path('customer/',            views.customer_review_view, name='customer'),
    path('customer/engagement/', views.customer_engagement,  name='customer_engagement'),
    path('customer/<int:customer_id>/sentiments/', views.customer_sentiments, name='customer_sentiments'),

    # ── Inventory / Audit ─────────────────────────────────────────────
    path('inventory/', views.inventory, name='inventory'),
    path('audit/',     views.audit,     name='audit'),

    # ── Reports & analytics ───────────────────────────────────────────
    path('reports/',        views.report_and_recommendations, name='reports'),
    path('benchmark/',      views.performance_benchmark,      name='performance_benchmark'),
    path('market/trends/',  views.market_industry_trends,     name='market_trends'),
    path('insights/',       views.insights_view,              name='insights'),
]