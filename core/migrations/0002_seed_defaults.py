from django.db import migrations


PRODUCTS = [
    ("Aluminum Window", "aluminum_window", "aluminum", "1.15"),
    ("Aluminum Door", "aluminum_door", "aluminum", "1.20"),
    ("Aluminum Partition", "aluminum_partition", "aluminum", "1.10"),
    ("Aluminum Frame", "aluminum_frame", "aluminum", "1.05"),
    ("Aluminum Rack", "aluminum_rack", "aluminum", "1.00"),
    ("Wooden Bed", "wooden_bed", "furniture", "1.30"),
    ("Sofa", "sofa", "furniture", "1.40"),
    ("Table", "table", "furniture", "1.10"),
    ("Chair", "chair", "furniture", "0.90"),
    ("Wardrobe", "wardrobe", "furniture", "1.25"),
    ("Kitchen Cabinet", "kitchen_cabinet", "furniture", "1.30"),
    ("Office Furniture", "office_furniture", "furniture", "1.20"),
    ("Custom Design", "custom_design", "both", "1.00"),
]


def seed_defaults(apps, schema_editor):
    Product = apps.get_model("core", "Product")
    Group = apps.get_model("auth", "Group")

    for name in ["Admin", "Staff", "Worker"]:
        Group.objects.get_or_create(name=name)

    for name, category, order_type, factor in PRODUCTS:
        Product.objects.get_or_create(
            name=name,
            defaults={
                "category": category,
                "order_type": order_type,
                "default_rate": 0,
                "material_factor": factor,
                "is_active": True,
            },
        )


def unseed_defaults(apps, schema_editor):
    Product = apps.get_model("core", "Product")
    Product.objects.filter(name__in=[product[0] for product in PRODUCTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_defaults, unseed_defaults),
    ]
