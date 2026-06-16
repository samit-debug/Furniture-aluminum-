import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from core.models import BusinessProfile


class Command(BaseCommand):
    help = "Create/update the default RRV admin account and business profile."

    def handle(self, *args, **options):
        username = os.environ.get("RRV_ADMIN_USERNAME", "rajesh")
        email = os.environ.get("RRV_ADMIN_EMAIL", "samitkumarrai948@gmail.com")
        password = os.environ.get("RRV_ADMIN_PASSWORD", "vikas&rakesh")

        for group_name in ["Admin", "Staff", "Worker"]:
            Group.objects.get_or_create(name=group_name)

        User = get_user_model()
        user, _created = User.objects.get_or_create(username=username)
        user.email = email
        user.first_name = "Rajesh"
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        user.groups.add(Group.objects.get(name="Admin"))

        demo_user = User.objects.filter(username="admin").exclude(pk=user.pk).first()
        if demo_user:
            demo_user.is_active = False
            demo_user.save(update_fields=["is_active"])

        profile = BusinessProfile.get_solo()
        profile.shop_name = "RRV furniture & aluminum workers"
        profile.owner_name = "Rajesh"
        profile.email = email
        profile.save()

        self.stdout.write(self.style.SUCCESS(f"Admin ready: {username} ({email})"))
