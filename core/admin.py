from django.contrib import admin

from .models import (
    BusinessProfile,
    Customer,
    Invoice,
    Measurement,
    Order,
    Payment,
    Product,
    Report,
    Stock,
    WorkAssignment,
    Worker,
)


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "owner_name", "mobile", "email", "updated_at")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "mobile", "email", "created_at")
    search_fields = ("name", "mobile", "email")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "order_type",
        "default_rate",
        "material_factor",
        "show_on_website",
        "featured",
        "is_active",
    )
    list_filter = ("category", "order_type", "show_on_website", "featured", "is_active")
    search_fields = ("name",)


class MeasurementInline(admin.StackedInline):
    model = Measurement
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class WorkAssignmentInline(admin.TabularInline):
    model = WorkAssignment
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "product_name",
        "quantity",
        "delivery_date",
        "status",
        "net_total",
        "paid_amount",
        "remaining_amount",
    )
    list_filter = ("status", "order_type", "delivery_date")
    search_fields = ("customer__name", "customer__mobile", "product_name", "design_type")
    inlines = [MeasurementInline, WorkAssignmentInline, PaymentInline]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("material_name", "category", "quantity", "unit", "low_stock_limit", "is_low_stock")
    list_filter = ("category",)
    search_fields = ("material_name",)


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ("name", "mobile", "skill", "wage_type", "wage_amount", "payment_due", "is_active")
    list_filter = ("skill", "wage_type", "is_active")
    search_fields = ("name", "mobile")


@admin.register(WorkAssignment)
class WorkAssignmentAdmin(admin.ModelAdmin):
    list_display = ("order", "worker", "start_date", "expected_finish_date", "status")
    list_filter = ("status", "worker__skill")
    search_fields = ("order__product_name", "worker__name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "method", "payment_date", "reference_number")
    list_filter = ("method", "payment_date")
    search_fields = ("order__customer__name", "order__product_name", "reference_number")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "order", "issue_date", "final_total")
    search_fields = ("invoice_number", "order__customer__name", "order__product_name")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "report_type", "period_start", "period_end", "generated_by", "created_at")
    list_filter = ("report_type", "created_at")
    search_fields = ("title", "notes")
