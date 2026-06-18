from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from django.utils import timezone


User = get_user_model()


MONEY_ZERO = Decimal("0.00")


PRODUCT_CATEGORY_CHOICES = [
    ("aluminum_window", "Aluminum Window"),
    ("aluminum_door", "Aluminum Door"),
    ("aluminum_partition", "Aluminum Partition"),
    ("aluminum_frame", "Aluminum Frame"),
    ("aluminum_rack", "Aluminum Rack"),
    ("wooden_bed", "Wooden Bed"),
    ("sofa", "Sofa"),
    ("table", "Table"),
    ("chair", "Chair"),
    ("wardrobe", "Wardrobe"),
    ("kitchen_cabinet", "Kitchen Cabinet"),
    ("office_furniture", "Office Furniture"),
    ("custom_design", "Custom Design"),
]


class Customer(models.Model):
    name = models.CharField(max_length=120)
    mobile = models.CharField(max_length=20)
    address = models.TextField()
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.mobile})"

    @property
    def pending_payment(self):
        return sum((order.remaining_amount for order in self.orders.all()), MONEY_ZERO)


class BusinessProfile(models.Model):
    shop_name = models.CharField(max_length=160, default="RRV furniture & aluminum workers")
    owner_name = models.CharField(max_length=120, default="Rajesh")
    tagline = models.CharField(
        max_length=220,
        default="Furniture, aluminum, glass and custom interior work across India.",
    )
    mobile = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    service_area = models.CharField(max_length=180, default="All India service available")
    gst_number = models.CharField(max_length=40, blank=True)
    upi_id = models.CharField(max_length=80, blank=True)
    bank_name = models.CharField(max_length=120, blank=True)
    account_holder_name = models.CharField(max_length=120, blank=True)
    account_number = models.CharField(max_length=40, blank=True)
    ifsc_code = models.CharField(max_length=20, blank=True)
    payment_qr = models.FileField(upload_to="business/payments/", blank=True)
    show_payment_details = models.BooleanField(default=True)
    logo = models.FileField(upload_to="business/", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Business Profile"
        verbose_name_plural = "Business Profile"

    def __str__(self):
        return self.shop_name

    @classmethod
    def get_solo(cls):
        profile, _created = cls.objects.get_or_create(pk=1)
        return profile


class TeamContact(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("manager", "Manager"),
        ("site_supervisor", "Site Supervisor"),
        ("billing", "Billing"),
        ("support", "Support"),
    ]

    name = models.CharField(max_length=120)
    mobile = models.CharField(max_length=20)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="support")
    whatsapp_enabled = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)
    show_on_website = models.BooleanField(default=True)
    notes = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["-is_primary", "name"]

    def __str__(self):
        return f"{self.name} - {self.mobile}"


class PublicEnquiry(models.Model):
    STATUS_NEW = "new"
    STATUS_CONTACTED = "contacted"
    STATUS_QUOTED = "quoted"
    STATUS_CONVERTED = "converted"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_CONTACTED, "Contacted"),
        (STATUS_QUOTED, "Quoted"),
        (STATUS_CONVERTED, "Converted"),
        (STATUS_CLOSED, "Closed"),
    ]

    name = models.CharField(max_length=120)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    city = models.CharField(max_length=120)
    service_required = models.CharField(max_length=40, choices=PRODUCT_CATEGORY_CHOICES)
    message = models.TextField(blank=True)
    preferred_contact = models.CharField(
        max_length=20,
        choices=[("call", "Call"), ("whatsapp", "WhatsApp"), ("email", "Email")],
        default="call",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Public enquiries"

    def __str__(self):
        return f"{self.name} - {self.get_service_required_display()}"


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, related_name="password_reset_otps", on_delete=models.CASCADE)
    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP for {self.email}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at


class Product(models.Model):
    ORDER_TYPE_ALUMINUM = "aluminum"
    ORDER_TYPE_FURNITURE = "furniture"
    ORDER_TYPE_BOTH = "both"

    ORDER_TYPE_CHOICES = [
        (ORDER_TYPE_ALUMINUM, "Aluminum"),
        (ORDER_TYPE_FURNITURE, "Furniture"),
        (ORDER_TYPE_BOTH, "Both"),
    ]

    CATEGORY_CHOICES = PRODUCT_CATEGORY_CHOICES

    name = models.CharField(max_length=120)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    description = models.TextField(blank=True)
    image = models.FileField(upload_to="products/", blank=True)
    default_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    material_factor = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=1,
        help_text="Approx material multiplier used after area calculation.",
    )
    show_on_website = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_READY = "ready"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_READY, "Ready"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    ORDER_TYPE_CHOICES = Product.ORDER_TYPE_CHOICES

    customer = models.ForeignKey(Customer, related_name="orders", on_delete=models.CASCADE)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    product_name = models.CharField(max_length=120)
    design_type = models.CharField(max_length=120, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    delivery_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    advance_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} - {self.customer.name} - {self.product_name}"

    @property
    def gst_amount(self):
        if not self.gst_percent:
            return MONEY_ZERO
        return ((self.total_amount - self.discount) * self.gst_percent / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @property
    def net_total(self):
        return max(self.total_amount - self.discount + self.gst_amount, MONEY_ZERO)

    @property
    def recorded_payments(self):
        return self.payments.aggregate(total=Sum("amount"))["total"] or MONEY_ZERO

    @property
    def paid_amount(self):
        return self.advance_payment + self.recorded_payments

    @property
    def remaining_amount(self):
        return max(self.net_total - self.paid_amount, MONEY_ZERO)

    @property
    def payment_status(self):
        if self.paid_amount <= MONEY_ZERO:
            return "Unpaid"
        if self.remaining_amount > MONEY_ZERO:
            return "Partial"
        return "Paid"


class Measurement(models.Model):
    UNIT_FEET = "feet"
    UNIT_INCH = "inch"
    UNIT_MM = "mm"

    UNIT_CHOICES = [
        (UNIT_FEET, "Feet"),
        (UNIT_INCH, "Inch"),
        (UNIT_MM, "MM"),
    ]

    order = models.OneToOneField(Order, related_name="measurement", on_delete=models.CASCADE)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    thickness = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default=UNIT_FEET)
    area_sqft = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    material_required = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Measurement for order #{self.order_id}"

    def save(self, *args, **kwargs):
        length_ft = self._to_feet(self.length)
        width_ft = self._to_feet(self.width)
        area = length_ft * width_ft * self.order.quantity
        factor = self.order.product.material_factor if self.order.product else Decimal("1.00")
        self.area_sqft = area.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.material_required = (area * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def _to_feet(self, value):
        if self.unit == self.UNIT_INCH:
            return value / Decimal("12")
        if self.unit == self.UNIT_MM:
            return value * Decimal("0.00328084")
        return value


class Stock(models.Model):
    CATEGORY_ALUMINUM = "aluminum"
    CATEGORY_FURNITURE = "furniture"
    CATEGORY_OTHER = "other"

    CATEGORY_CHOICES = [
        (CATEGORY_ALUMINUM, "Aluminum"),
        (CATEGORY_FURNITURE, "Furniture"),
        (CATEGORY_OTHER, "Other"),
    ]

    material_name = models.CharField(max_length=120)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit = models.CharField(max_length=30, default="pcs")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    low_stock_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "material_name"]

    def __str__(self):
        return self.material_name

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_limit


class Worker(models.Model):
    SKILL_CHOICES = [
        ("carpenter", "Carpenter"),
        ("aluminum_fitter", "Aluminum Fitter"),
        ("painter", "Painter"),
        ("helper", "Helper"),
    ]
    WAGE_TYPE_CHOICES = [
        ("daily", "Daily Wage"),
        ("monthly", "Monthly Salary"),
    ]

    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=120)
    mobile = models.CharField(max_length=20)
    skill = models.CharField(max_length=30, choices=SKILL_CHOICES)
    wage_type = models.CharField(max_length=20, choices=WAGE_TYPE_CHOICES, default="daily")
    wage_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.get_skill_display()}"


class WorkAssignment(models.Model):
    STATUS_ASSIGNED = "assigned"
    STATUS_WORKING = "working"
    STATUS_COMPLETED = "completed"
    STATUS_HOLD = "hold"

    STATUS_CHOICES = [
        (STATUS_ASSIGNED, "Assigned"),
        (STATUS_WORKING, "Working"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_HOLD, "Hold"),
    ]

    order = models.ForeignKey(Order, related_name="assignments", on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, related_name="assignments", on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.localdate)
    expected_finish_date = models.DateField(null=True, blank=True)
    actual_finish_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ASSIGNED)
    remarks = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.order.product_name} -> {self.worker.name}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("upi", "UPI"),
        ("bank_transfer", "Bank Transfer"),
        ("cheque", "Cheque"),
    ]

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    payment_date = models.DateField(default=timezone.localdate)
    reference_number = models.CharField(max_length=80, blank=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ["-payment_date", "-id"]

    def __str__(self):
        return f"{self.order} - {self.amount}"


class FinancialTransaction(models.Model):
    TYPE_INCOME = "income"
    TYPE_EXPENSE = "expense"
    TYPE_CHOICES = [
        (TYPE_INCOME, "Income / Received"),
        (TYPE_EXPENSE, "Expense / Paid"),
    ]

    CATEGORY_CHOICES = [
        ("customer_payment", "Customer Payment"),
        ("advance", "Advance"),
        ("worker_wage", "Worker Wage"),
        ("material_purchase", "Material Purchase"),
        ("supplier_payment", "Supplier Payment"),
        ("refund", "Refund"),
        ("transport", "Transport"),
        ("rent", "Rent"),
        ("electricity", "Electricity"),
        ("maintenance", "Maintenance"),
        ("other", "Other"),
    ]

    METHOD_CHOICES = Payment.METHOD_CHOICES + [("online_gateway", "Online Gateway")]

    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=140)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=30, choices=METHOD_CHOICES)
    transaction_date = models.DateField(default=timezone.localdate)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    worker = models.ForeignKey(Worker, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    party_name = models.CharField(max_length=120, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    attachment = models.FileField(upload_to="transactions/", blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transaction_date", "-id"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.title} - {self.amount}"


class Invoice(models.Model):
    order = models.OneToOneField(Order, related_name="invoice", on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=30, unique=True, blank=True)
    issue_date = models.DateField(default=timezone.localdate)
    final_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-issue_date", "-id"]

    def __str__(self):
        return self.invoice_number or f"Invoice for order #{self.order_id}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            today = timezone.localdate()
            count = Invoice.objects.filter(issue_date=today).count() + 1
            self.invoice_number = f"INV-{today:%Y%m%d}-{count:04d}"
        self.final_total = self.order.net_total
        super().save(*args, **kwargs)


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ("daily_sales", "Daily Sales Report"),
        ("monthly_sales", "Monthly Sales Report"),
        ("profit_loss", "Profit/Loss Report"),
        ("pending_orders", "Pending Orders"),
        ("completed_orders", "Completed Orders"),
        ("pending_payment", "Pending Payment"),
        ("stock", "Stock Report"),
        ("worker", "Worker Report"),
    ]

    title = models.CharField(max_length=150)
    report_type = models.CharField(max_length=40, choices=REPORT_TYPE_CHOICES)
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    generated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
