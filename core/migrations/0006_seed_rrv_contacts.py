from django.db import migrations


CONTACTS = [
    ("Rajesh Kumar", "9794491007", "owner", True),
    ("Vikas Rai", "8737878916", "manager", False),
    ("Rakesh Rai", "9598909275", "site_supervisor", False),
]


def seed_contacts(apps, schema_editor):
    BusinessProfile = apps.get_model("core", "BusinessProfile")
    TeamContact = apps.get_model("core", "TeamContact")

    profile, _created = BusinessProfile.objects.get_or_create(pk=1)
    profile.shop_name = "RRV furniture & aluminum workers"
    profile.owner_name = "Rajesh Kumar"
    profile.mobile = "9794491007"
    profile.whatsapp_number = "919794491007"
    profile.tagline = "Furniture, aluminum, glass and custom interior work across India."
    profile.service_area = "All India service available"
    profile.show_payment_details = True
    profile.save()

    for name, mobile, role, is_primary in CONTACTS:
        TeamContact.objects.get_or_create(
            mobile=mobile,
            defaults={
                "name": name,
                "role": role,
                "is_primary": is_primary,
                "whatsapp_enabled": True,
                "show_on_website": True,
            },
        )


def unseed_contacts(apps, schema_editor):
    TeamContact = apps.get_model("core", "TeamContact")
    TeamContact.objects.filter(mobile__in=[contact[1] for contact in CONTACTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_publicenquiry_teamcontact_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_contacts, unseed_contacts),
    ]
