import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import random
import re

import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "supplyinsights.settings")
django.setup()

from app.models import MarketTrend  # Update to your app name
from faker import Faker
from app.models import Supplier
import random
import string

fake = Faker()

companies = [
    "Irvines",
    "Delta Beverages",
    "Gloria",
    "Varun Beverages",
    "Dairiboard",
    "Cairns"
]

def supplier_code():
    return "SUP-" + "".join(random.choices(string.digits, k=5))

def create_suppliers():
    for company in companies:
        Supplier.objects.create(
            supplier_code=supplier_code(),
            name=fake.company(),
            company_name=company,
            contact_person=fake.name(),
            email=fake.company_email(),
            phone=fake.phone_number(),
            location=fake.city(),
            tax_number=fake.bothify(text="TAX-#####"),
            registration_number=fake.bothify(text="REG-#####"),
            is_active=True
        )

    print("Suppliers created ✔")

