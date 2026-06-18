from django.db import migrations


PRODUCTS = [
    (
        "Premium Aluminum Sliding Window",
        "aluminum_window",
        "aluminum",
        "Smooth sliding aluminum window with glass fitting, lock, handle and custom size option.",
    ),
    (
        "Aluminum Glass Door",
        "aluminum_door",
        "aluminum",
        "Shop, office and home aluminum glass door work with clean frame finishing.",
    ),
    (
        "Office Glass Partition",
        "aluminum_partition",
        "aluminum",
        "Modern aluminum and glass partition for office, showroom and cabin spaces.",
    ),
    (
        "Custom Wooden Bed",
        "wooden_bed",
        "furniture",
        "Strong wooden bed made to measurement with storage and polish options.",
    ),
    (
        "Wardrobe & Kitchen Cabinet",
        "wardrobe",
        "furniture",
        "Wardrobe, kitchen cabinet and storage units with laminate, hinges and drawer channels.",
    ),
    (
        "Sofa, Table & Office Furniture",
        "sofa",
        "both",
        "Home and office furniture with foam, fabric, wood and custom design support.",
    ),
]


def seed_products(apps, schema_editor):
    Product = apps.get_model("core", "Product")
    for name, category, order_type, description in PRODUCTS:
        Product.objects.get_or_create(
            name=name,
            defaults={
                "category": category,
                "order_type": order_type,
                "description": description,
                "default_rate": 0,
                "material_factor": 1,
                "show_on_website": True,
                "featured": True,
                "is_active": True,
            },
        )


def unseed_products(apps, schema_editor):
    Product = apps.get_model("core", "Product")
    Product.objects.filter(name__in=[product[0] for product in PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_seed_rrv_contacts"),
    ]

    operations = [
        migrations.RunPython(seed_products, unseed_products),
    ]
