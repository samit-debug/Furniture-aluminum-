from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView
from django.conf import settings
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import (
    BusinessProfileForm,
    CustomerForm,
    InvoiceForm,
    MeasurementForm,
    OrderForm,
    PaymentForm,
    ProductForm,
    ReportForm,
    StockForm,
    WorkAssignmentForm,
    WorkerForm,
)
from .models import (
    BusinessProfile,
    Customer,
    Invoice,
    Order,
    Payment,
    Product,
    Report,
    Stock,
    WorkAssignment,
    Worker,
)


def is_worker_user(user):
    return user.groups.filter(name__iexact="Worker").exists()


def get_worker_profile(user):
    try:
        return user.worker
    except Worker.DoesNotExist:
        return None


def is_admin_role(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name__iexact="Admin").exists())


def is_staff_role(user):
    return user.is_authenticated and (
        is_admin_role(user) or user.is_staff or user.groups.filter(name__iexact="Staff").exists()
    )


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_staff_role(self.request.user)


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_admin_role(self.request.user)


class RRVPasswordResetView(PasswordResetView):
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    template_name = "registration/password_reset_form.html"
    success_url = reverse_lazy("password_reset_done")

    def form_valid(self, form):
        response = super().form_valid(form)
        if settings.DEBUG:
            links = []
            for user in form.get_users(form.cleaned_data["email"]):
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                path = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
                links.append(self.request.build_absolute_uri(path))
            self.request.session["debug_reset_links"] = links
        return response


class RRVPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["debug_reset_links"] = self.request.session.get("debug_reset_links", [])
        return context


class ERPListView(LoginRequiredMixin, ListView):
    paginate_by = 15
    search_fields = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q", "").strip()
        if query and self.search_fields:
            search_query = Q()
            for field in self.search_fields:
                search_query |= Q(**{f"{field}__icontains": query})
            queryset = queryset.filter(search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


@login_required
def dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    orders = Order.objects.select_related("customer", "product")

    if is_worker_user(request.user):
        worker = get_worker_profile(request.user)
        orders = orders.filter(assignments__worker=worker).distinct() if worker else orders.none()

    payments = Payment.objects.all()
    today_sale = payments.filter(payment_date=today).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    monthly_sale = (
        payments.filter(payment_date__gte=month_start, payment_date__lte=today).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )
    pending_payment = sum((order.remaining_amount for order in orders), Decimal("0.00"))

    status_counts = {
        status: orders.filter(status=status).count()
        for status, _label in Order.STATUS_CHOICES
    }

    context = {
        "total_customers": Customer.objects.count(),
        "total_orders": orders.count(),
        "pending_orders": status_counts.get(Order.STATUS_PENDING, 0),
        "working_orders": status_counts.get(Order.STATUS_IN_PROGRESS, 0),
        "ready_orders": status_counts.get(Order.STATUS_READY, 0),
        "delivered_orders": status_counts.get(Order.STATUS_DELIVERED, 0),
        "today_sale": today_sale,
        "monthly_sale": monthly_sale,
        "pending_payment": pending_payment,
        "low_stock_items": [item for item in Stock.objects.all() if item.is_low_stock],
        "recent_orders": orders[:8],
        "recent_payments": payments.select_related("order", "order__customer")[:6],
    }
    return render(request, "core/dashboard.html", context)


@login_required
@user_passes_test(is_admin_role)
def admin_control(request):
    return redirect("dashboard")


def public_catalog(request):
    products = Product.objects.filter(is_active=True, show_on_website=True).order_by("-featured", "category", "name")
    context = {
        "products": products,
        "featured_products": products.filter(featured=True)[:6],
        "business_profile": BusinessProfile.get_solo(),
    }
    return render(request, "core/public_catalog.html", context)


@login_required
@user_passes_test(is_admin_role)
def business_settings(request):
    profile = BusinessProfile.get_solo()
    form = BusinessProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Business settings updated successfully.")
        return redirect("business-settings")
    return render(
        request,
        "core/form.html",
        {"form": form, "title": "Business Settings", "submit_label": "Update Settings"},
    )


class CustomerListView(StaffRequiredMixin, ERPListView):
    model = Customer
    template_name = "core/customer_list.html"
    context_object_name = "customers"
    search_fields = ("name", "mobile", "email", "address")


class CustomerDetailView(StaffRequiredMixin, DetailView):
    model = Customer
    template_name = "core/customer_detail.html"
    context_object_name = "customer"


class CustomerCreateView(StaffRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "core/form.html"
    success_url = reverse_lazy("customer-list")
    extra_context = {"title": "Add Customer", "submit_label": "Save Customer"}

    def form_valid(self, form):
        messages.success(self.request, "Customer saved successfully.")
        return super().form_valid(form)


class CustomerUpdateView(StaffRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "core/form.html"
    success_url = reverse_lazy("customer-list")
    extra_context = {"title": "Edit Customer", "submit_label": "Update Customer"}

    def form_valid(self, form):
        messages.success(self.request, "Customer updated successfully.")
        return super().form_valid(form)


class ProductListView(StaffRequiredMixin, ERPListView):
    model = Product
    template_name = "core/product_list.html"
    context_object_name = "products"
    search_fields = ("name", "category", "order_type")


class ProductCreateView(AdminRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "core/form.html"
    success_url = reverse_lazy("product-list")
    extra_context = {"title": "Add Product", "submit_label": "Save Product"}


class ProductUpdateView(AdminRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "core/form.html"
    success_url = reverse_lazy("product-list")
    extra_context = {"title": "Edit Product", "submit_label": "Update Product"}


class OrderListView(ERPListView):
    model = Order
    template_name = "core/order_list.html"
    context_object_name = "orders"
    search_fields = ("customer__name", "customer__mobile", "product_name", "design_type")

    def get_queryset(self):
        queryset = super().get_queryset().select_related("customer", "product")
        status = self.request.GET.get("status", "").strip()
        if status:
            queryset = queryset.filter(status=status)
        if is_worker_user(self.request.user):
            worker = get_worker_profile(self.request.user)
            queryset = queryset.filter(assignments__worker=worker).distinct() if worker else queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "").strip()
        context["status_choices"] = Order.STATUS_CHOICES
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "core/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        queryset = Order.objects.select_related("customer", "product").prefetch_related("payments", "assignments")
        if is_worker_user(self.request.user):
            worker = get_worker_profile(self.request.user)
            return queryset.filter(assignments__worker=worker).distinct() if worker else queryset.none()
        return queryset


class OrderCreateView(StaffRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "core/form.html"
    success_url = reverse_lazy("order-list")
    extra_context = {"title": "Add Order", "submit_label": "Save Order"}

    def form_valid(self, form):
        messages.success(self.request, "Order saved. Add measurement when ready.")
        return super().form_valid(form)


class OrderUpdateView(StaffRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "core/form.html"
    extra_context = {"title": "Edit Order", "submit_label": "Update Order"}

    def get_success_url(self):
        return reverse_lazy("order-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Order updated successfully.")
        return super().form_valid(form)


@login_required
@user_passes_test(is_staff_role)
def measurement_form(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    measurement = getattr(order, "measurement", None)
    form = MeasurementForm(request.POST or None, instance=measurement)
    if request.method == "POST" and form.is_valid():
        instance = form.save(commit=False)
        instance.order = order
        instance.save()
        messages.success(request, "Measurement saved and material requirement recalculated.")
        return redirect("order-detail", pk=order.pk)

    return render(
        request,
        "core/form.html",
        {
            "form": form,
            "title": f"Measurement - Order #{order.pk}",
            "submit_label": "Save Measurement",
        },
    )


class StockListView(AdminRequiredMixin, ERPListView):
    model = Stock
    template_name = "core/stock_list.html"
    context_object_name = "stocks"
    search_fields = ("material_name", "category", "unit")


class StockCreateView(AdminRequiredMixin, CreateView):
    model = Stock
    form_class = StockForm
    template_name = "core/form.html"
    success_url = reverse_lazy("stock-list")
    extra_context = {"title": "Add Stock Item", "submit_label": "Save Stock"}


class StockUpdateView(AdminRequiredMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = "core/form.html"
    success_url = reverse_lazy("stock-list")
    extra_context = {"title": "Edit Stock Item", "submit_label": "Update Stock"}


class WorkerListView(AdminRequiredMixin, ERPListView):
    model = Worker
    template_name = "core/worker_list.html"
    context_object_name = "workers"
    search_fields = ("name", "mobile", "skill")


class WorkerCreateView(AdminRequiredMixin, CreateView):
    model = Worker
    form_class = WorkerForm
    template_name = "core/form.html"
    success_url = reverse_lazy("worker-list")
    extra_context = {"title": "Add Worker", "submit_label": "Save Worker"}


class WorkerUpdateView(AdminRequiredMixin, UpdateView):
    model = Worker
    form_class = WorkerForm
    template_name = "core/form.html"
    success_url = reverse_lazy("worker-list")
    extra_context = {"title": "Edit Worker", "submit_label": "Update Worker"}


class AssignmentListView(ERPListView):
    model = WorkAssignment
    template_name = "core/assignment_list.html"
    context_object_name = "assignments"
    search_fields = ("order__product_name", "order__customer__name", "worker__name")

    def get_queryset(self):
        queryset = super().get_queryset().select_related("order", "order__customer", "worker")
        if is_worker_user(self.request.user):
            worker = get_worker_profile(self.request.user)
            queryset = queryset.filter(worker=worker) if worker else queryset.none()
        return queryset


class AssignmentCreateView(AdminRequiredMixin, CreateView):
    model = WorkAssignment
    form_class = WorkAssignmentForm
    template_name = "core/form.html"
    success_url = reverse_lazy("assignment-list")
    extra_context = {"title": "Assign Work", "submit_label": "Save Assignment"}


class AssignmentUpdateView(AdminRequiredMixin, UpdateView):
    model = WorkAssignment
    form_class = WorkAssignmentForm
    template_name = "core/form.html"
    success_url = reverse_lazy("assignment-list")
    extra_context = {"title": "Edit Work Assignment", "submit_label": "Update Assignment"}


class PaymentListView(StaffRequiredMixin, ERPListView):
    model = Payment
    template_name = "core/payment_list.html"
    context_object_name = "payments"
    search_fields = ("order__customer__name", "order__product_name", "reference_number")

    def get_queryset(self):
        return super().get_queryset().select_related("order", "order__customer")


class PaymentCreateView(StaffRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = "core/form.html"
    success_url = reverse_lazy("payment-list")
    extra_context = {"title": "Record Payment", "submit_label": "Save Payment"}


@login_required
@user_passes_test(is_staff_role)
def payment_for_order(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    form = PaymentForm(request.POST or None, initial={"order": order})
    form.fields["order"].disabled = True
    if request.method == "POST" and form.is_valid():
        payment = form.save(commit=False)
        payment.order = order
        payment.save()
        messages.success(request, "Payment recorded successfully.")
        return redirect("order-detail", pk=order.pk)
    return render(
        request,
        "core/form.html",
        {"form": form, "title": f"Payment - Order #{order.pk}", "submit_label": "Save Payment"},
    )


class InvoiceListView(StaffRequiredMixin, ERPListView):
    model = Invoice
    template_name = "core/invoice_list.html"
    context_object_name = "invoices"
    search_fields = ("invoice_number", "order__customer__name", "order__product_name")

    def get_queryset(self):
        return super().get_queryset().select_related("order", "order__customer")


class InvoiceDetailView(StaffRequiredMixin, DetailView):
    model = Invoice
    template_name = "core/invoice_detail.html"
    context_object_name = "invoice"

    def get_queryset(self):
        return Invoice.objects.select_related("order", "order__customer", "order__product")


class InvoiceCreateView(StaffRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "core/form.html"
    success_url = reverse_lazy("invoice-list")
    extra_context = {"title": "Create Invoice", "submit_label": "Generate Invoice"}


@login_required
@user_passes_test(is_staff_role)
def invoice_for_order(request, order_pk):
    order = get_object_or_404(Order, pk=order_pk)
    invoice = getattr(order, "invoice", None)
    if invoice:
        return redirect("invoice-detail", pk=invoice.pk)
    invoice = Invoice.objects.create(order=order)
    messages.success(request, "Invoice generated successfully.")
    return redirect("invoice-detail", pk=invoice.pk)


class ReportListView(StaffRequiredMixin, ERPListView):
    model = Report
    template_name = "core/report_list.html"
    context_object_name = "reports"
    search_fields = ("title", "report_type", "notes")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        month_start = today.replace(day=1)
        context["daily_sales"] = Payment.objects.filter(payment_date=today).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        context["monthly_sales"] = (
            Payment.objects.filter(payment_date__gte=month_start, payment_date__lte=today).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        context["pending_orders"] = Order.objects.filter(status__in=[Order.STATUS_PENDING, Order.STATUS_IN_PROGRESS]).count()
        context["completed_orders"] = Order.objects.filter(status=Order.STATUS_DELIVERED).count()
        context["pending_payment"] = sum((order.remaining_amount for order in Order.objects.all()), Decimal("0.00"))
        context["low_stock_count"] = sum(1 for item in Stock.objects.all() if item.is_low_stock)
        return context


class ReportCreateView(StaffRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = "core/form.html"
    success_url = reverse_lazy("report-list")
    extra_context = {"title": "Save Report Note", "submit_label": "Save Report"}

    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        return super().form_valid(form)
