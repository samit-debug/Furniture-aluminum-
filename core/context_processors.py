from .models import BusinessProfile
from django.conf import settings


def business_profile(request):
    user = getattr(request, "user", None)
    is_admin_role = bool(
        user
        and user.is_authenticated
        and (user.is_superuser or user.groups.filter(name__iexact="Admin").exists())
    )
    is_staff_role = bool(
        user
        and user.is_authenticated
        and (is_admin_role or user.is_staff or user.groups.filter(name__iexact="Staff").exists())
    )
    return {
        "business_profile": BusinessProfile.get_solo(),
        "is_admin_role": is_admin_role,
        "is_staff_role": is_staff_role,
        "debug": settings.DEBUG,
    }
