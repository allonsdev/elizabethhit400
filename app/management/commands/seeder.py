from django.core.management.base import BaseCommand
from faker import Faker
from app.models import Supplier
import random
import string


class Command(BaseCommand):
    help = "Generate fake supplier data"

    def handle(self, *args, **kwargs):
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
            while True:
                code = "SUP-" + "".join(random.choices(string.digits, k=5))
                if not Supplier.objects.filter(supplier_code=code).exists():
                    return code

        created_count = 0

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
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"{created_count} suppliers created successfully ✔")
        )