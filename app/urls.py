from django.urls import path

from . import views


urlpatterns = [
    # Authentication
    path('', views.home_view, name='home'),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Example protected routes
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("admin/dashboard/", views.admin_dashboard_view, name="admin_dashboard"),
    path("insights/", views.insights_view, name="insights"),
    path("inventory/", views.inventory_view, name="inventory"),
    # path("supplier/<int:supplier_id>/reviews/", views.supplier_reviews, name="supplier_reviews"),
    
    # path("customer/<int:customer_id>/reviews/", views.customer_reviews, name="customer_reviews"),
    path("suppliers/manage/", views.supplier_management, name="supplier_manage"),
    path("supplier/<int:supplier_id>/sentiments/", views.supplier_sentiments, name="supplier_sentiments"),
    path("customer/<int:customer_id>/sentiments/", views.customer_sentiments, name="customer_sentiments"),
    path("customer/engagement/", views.customer_engagement, name="customer_engagement"),
    path("inventory/", views.store_inventory, name="store_inventory"),
    path("customer/", views.customer_review_view, name="customer"),
    path("reports/", views.report_and_recommendations, name="reports"),
    path("benchmark/", views.performance_benchmark, name="performance_benchmark"),
    path("market/trends/", views.market_industry_trends, name="market_trends"),
    
    
    path('register/', views.supplier_register, name='supplier_register'),
    path('delivery/', views.record_delivery, name='delivery'),
    path('review/', views.supplier_review, name='supplier_review'),
    path('complaint/', views.record_complaint, name='supplier_complaint'),
]

