from django import forms

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


class BootstrapModelForm(forms.ModelForm):
    date_fields = set()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if name in self.date_fields:
                widget.input_type = "date"
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class CustomerForm(BootstrapModelForm):
    class Meta:
        model = Customer
        fields = ["name", "mobile", "address", "email"]


class BusinessProfileForm(BootstrapModelForm):
    class Meta:
        model = BusinessProfile
        fields = ["shop_name", "owner_name", "mobile", "whatsapp_number", "email", "address", "gst_number", "logo"]


class ProductForm(BootstrapModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "order_type",
            "description",
            "image",
            "default_rate",
            "material_factor",
            "show_on_website",
            "featured",
            "is_active",
        ]


class OrderForm(BootstrapModelForm):
    date_fields = {"delivery_date"}

    class Meta:
        model = Order
        fields = [
            "customer",
            "order_type",
            "product",
            "product_name",
            "design_type",
            "quantity",
            "delivery_date",
            "total_amount",
            "discount",
            "gst_percent",
            "advance_payment",
            "status",
            "notes",
        ]


class MeasurementForm(BootstrapModelForm):
    class Meta:
        model = Measurement
        fields = ["length", "width", "height", "thickness", "unit", "notes"]


class StockForm(BootstrapModelForm):
    class Meta:
        model = Stock
        fields = [
            "material_name",
            "category",
            "quantity",
            "unit",
            "purchase_price",
            "selling_price",
            "low_stock_limit",
        ]


class WorkerForm(BootstrapModelForm):
    class Meta:
        model = Worker
        fields = ["user", "name", "mobile", "skill", "wage_type", "wage_amount", "payment_due", "is_active"]


class WorkAssignmentForm(BootstrapModelForm):
    date_fields = {"start_date", "expected_finish_date", "actual_finish_date"}

    class Meta:
        model = WorkAssignment
        fields = [
            "order",
            "worker",
            "start_date",
            "expected_finish_date",
            "actual_finish_date",
            "status",
            "remarks",
        ]


class PaymentForm(BootstrapModelForm):
    date_fields = {"payment_date"}

    class Meta:
        model = Payment
        fields = ["order", "amount", "method", "payment_date", "reference_number", "note"]


class InvoiceForm(BootstrapModelForm):
    date_fields = {"issue_date"}

    class Meta:
        model = Invoice
        fields = ["order", "issue_date", "notes"]


class ReportForm(BootstrapModelForm):
    date_fields = {"period_start", "period_end"}

    class Meta:
        model = Report
        fields = ["title", "report_type", "period_start", "period_end", "notes"]
