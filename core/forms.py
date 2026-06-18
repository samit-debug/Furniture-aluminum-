from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from .models import (
    BusinessProfile,
    Customer,
    FinancialTransaction,
    Invoice,
    Measurement,
    Order,
    Payment,
    PublicEnquiry,
    Product,
    Report,
    Stock,
    TeamContact,
    WorkAssignment,
    Worker,
)


class RRVAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email or Username",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "username",
                "placeholder": "email@example.com or username",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "current-password",
                "placeholder": "Enter password",
            }
        ),
    )
    error_messages = {
        "invalid_login": "Email/username ya password sahi nahi hai.",
        "inactive": "Ye account inactive hai.",
    }

    def clean_username(self):
        return self.cleaned_data["username"].strip()


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


class OTPPasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Registered Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
    )


class OTPPasswordResetVerifyForm(forms.Form):
    email = forms.EmailField(widget=forms.HiddenInput())
    code = forms.CharField(
        label="OTP",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "one-time-code"}),
    )
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )
    new_password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    def clean_code(self):
        return self.cleaned_data["code"].strip()

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("new_password1")
        password2 = cleaned.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("New password aur confirm password match nahi kar rahe.")
        if password1:
            validate_password(password1)
        return cleaned


class BusinessProfileForm(BootstrapModelForm):
    class Meta:
        model = BusinessProfile
        fields = [
            "shop_name",
            "owner_name",
            "tagline",
            "mobile",
            "whatsapp_number",
            "email",
            "address",
            "service_area",
            "gst_number",
            "upi_id",
            "bank_name",
            "account_holder_name",
            "account_number",
            "ifsc_code",
            "payment_qr",
            "show_payment_details",
            "logo",
        ]


class TeamContactForm(BootstrapModelForm):
    class Meta:
        model = TeamContact
        fields = ["name", "mobile", "role", "whatsapp_enabled", "is_primary", "show_on_website", "notes"]


class PublicEnquiryForm(BootstrapModelForm):
    class Meta:
        model = PublicEnquiry
        fields = ["name", "mobile", "email", "city", "service_required", "preferred_contact", "message"]


class PublicEnquiryAdminForm(BootstrapModelForm):
    class Meta:
        model = PublicEnquiry
        fields = ["name", "mobile", "email", "city", "service_required", "preferred_contact", "status", "admin_note"]


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


class FinancialTransactionForm(BootstrapModelForm):
    date_fields = {"transaction_date"}

    class Meta:
        model = FinancialTransaction
        fields = [
            "transaction_type",
            "category",
            "title",
            "amount",
            "method",
            "transaction_date",
            "customer",
            "worker",
            "order",
            "party_name",
            "reference_number",
            "attachment",
            "note",
        ]


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
