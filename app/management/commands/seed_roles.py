from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default groups and sample users for the SupplyInsights dashboard."

    def handle(self, *args, **options):
        User = get_user_model()

        groups = {
            "Administrator": [],
            "Management": [],
        }

        for group_name in groups.keys():
            group, created = Group.objects.get_or_create(name=group_name)
            action = "created" if created else "already exists"
            self.stdout.write(self.style.SUCCESS(f"Group '{group_name}' {action}"))

        sample_users = [
            {
                "username": "admin1",
                "email": "admin1@example.com",
                "password": "Admin123!",
                "is_superuser": True,
                "is_staff": True,
                "groups": ["Administrator"],
            },
            {
                "username": "manager1",
                "email": "manager1@example.com",
                "password": "Manager123!",
                "is_superuser": False,
                "is_staff": True,
                "groups": ["Management"],
            },
            {
                "username": "manager2",
                "email": "manager2@example.com",
                "password": "Manager123!",
                "is_superuser": False,
                "is_staff": True,
                "groups": ["Management"],
            },
            {
                "username": "analyst1",
                "email": "analyst1@example.com",
                "password": "Analyst123!",
                "is_superuser": False,
                "is_staff": True,
                "groups": ["Management"],
            },
            {
                "username": "inventory1",
                "email": "inventory1@example.com",
                "password": "Inventory123!",
                "is_superuser": False,
                "is_staff": True,
                "groups": ["Administrator"],
            },
        ]

        for user_data in sample_users:
            username = user_data["username"]
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": user_data["email"]}
            )
            if created:
                user.set_password(user_data["password"])
            user.is_superuser = user_data["is_superuser"]
            user.is_staff = user_data["is_staff"]
            user.save()

            for group_name in user_data["groups"]:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)

            self.stdout.write(
                self.style.SUCCESS(
                    f"User '{username}' {'created' if created else 'updated'} and assigned to {user_data['groups']}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Seeding complete."))

