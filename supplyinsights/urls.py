"""
URL configuration for supplyinsights project.
"""
from django.contrib import admin
from django.urls import include, path


# Customize Django admin branding
admin.site.site_header = "SupplyInsights Admin"
admin.site.site_title = "SupplyInsights Admin Portal"
admin.site.index_title = "SupplyInsights Management Dashboard"


urlpatterns = [
    path("admin/", admin.site.urls),
    # Main application URLs
    path("", include("app.urls")),
]

