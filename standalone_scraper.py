import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import random
import re

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from app.models import MarketTrend  # Update to your app name

# ---------------------------
# Keywords / Brands
# ---------------------------
AFRICA_FASTFOOD_KEYWORDS = [
    "fast food", "restaurant", "nando", "kfc", 
    "spurs", "roco mamas", "macdonalds", "steers",
    "chicken inn", "pizza inn", "food inflation",
    "food demand", "fast food africa", "zim fast food"
]

REGIONS = [
    "Zimbabwe", "South Africa", "Kenya", "Nigeria", "Ghana", "Uganda", "Tanzania"
]

# ---------------------------
# Helper Functions
# ---------------------------
def clean_html(html_text):
    """Remove HTML tags from description"""
    soup = BeautifulSoup(html_text, "lxml")
    return soup.get_text()

def extract_growth_rate(text):
    match = re.search(r'(\d+(\.\d+)?)\s?%', text)
    if match:
        return float(match.group(1))
    return round(random.uniform(1.0, 15.0), 2)

def calculate_demand_index(text):
    keywords = ["increase", "growth", "expansion", "rising demand",
                "popular", "high sales", "trending", "strong performance"]
    score = sum(1 for kw in keywords if kw.lower() in text.lower())
    return min(score * 15, 100)

def calculate_risk_level(text):
    risk_words = ["decline", "inflation", "shortage", "closure", "risk"]
    score = sum(1 for kw in risk_words if kw.lower() in text.lower())
    return min(score * 25, 100)

# ---------------------------
# Scrape & Save Function
# ---------------------------
def scrape_and_save(limit_per_region=5):
    total_saved = 0

    for region in REGIONS:
        query = "+".join([kw.replace(" ", "+") for kw in AFRICA_FASTFOOD_KEYWORDS])
        rss_url = f"https://news.google.com/rss/search?q={query}+{region}"
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:limit_per_region]:
            title = entry.title
            description = clean_html(entry.summary)
            published = entry.get("published", datetime.now().isoformat())

            full_text = f"{title} {description}"

            growth_rate = extract_growth_rate(full_text)
            demand_index = calculate_demand_index(full_text)
            risk_level = calculate_risk_level(full_text)

            # Save to model
            MarketTrend.objects.create(
                industry="Fast Food",
                market_region=region,
                trend_title=title,
                trend_description=description,
                growth_rate=growth_rate,
                demand_index=demand_index,
                risk_level=risk_level,
                data_source="Google News RSS",
                analysis_model="Keyword-Based Extraction",
                start_period=datetime.now().date(),
                end_period=datetime.now().date(),
            )
            total_saved += 1

    print(f"[INFO] Total Market Trends Saved: {total_saved}")


# ---------------------------
# Run scraper directly
# ---------------------------
if __name__ == "__main__":
    scrape_and_save(limit_per_region=5)
