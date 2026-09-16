from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin','Admin'), ('business_owner','Business Owner'),
        ('product_manager','Product Manager'), ('catalog_manager','Catalog Manager'),
        ('marketing_user','Marketing User'), ('viewer','Viewer'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='viewer')
    def __str__(self): return f'{self.user.username} - {self.get_role_display()}'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    class Meta: unique_together = ('category','name')
    def __str__(self): return f'{self.category.name} - {self.name}'

class CategoryAttribute(models.Model):
    FIELD_TYPES = [('text','Text'),('number','Number'),('boolean','Boolean'),('choice','Choice')]
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text')
    required = models.BooleanField(default=False)
    choices = models.JSONField(default=list, blank=True)
    class Meta: unique_together = ('category','name')
    def __str__(self): return f'{self.category.name}: {self.name}'

class Product(models.Model):
    LIFECYCLE = [('new','New'),('active','Active'),('high','High Performing'),('low','Low Performing'),('seasonal','Seasonal'),('out','Out of Stock'),('discontinued','Discontinued')]
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    subcategory = models.ForeignKey(SubCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    brand = models.CharField(max_length=150, blank=True)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    specifications = models.JSONField(default=dict, blank=True)
    inventory = models.PositiveIntegerField(default=0)
    lifecycle = models.CharField(max_length=20, choices=LIFECYCLE, default='new')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='products_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ai_product_type = models.CharField(max_length=150, blank=True, null=True)
    ai_category = models.CharField(max_length=150, blank=True, null=True)
    ai_subcategory = models.CharField(max_length=150, blank=True, null=True)
    ai_colors = models.JSONField(default=list, blank=True)
    ai_materials = models.JSONField(default=list, blank=True)
    ai_style = models.CharField(max_length=150, blank=True, null=True)
    ai_use_case = models.CharField(max_length=255, blank=True, null=True)
    ai_confidence = models.FloatField(null=True, blank=True)
    ai_uncertainty = models.TextField(blank=True, null=True)
    ai_observed_features = models.JSONField(default=list, blank=True)
    ai_attributes = models.JSONField(default=dict, blank=True)
    ai_title = models.CharField(max_length=300, blank=True)
    ai_short_description = models.TextField(blank=True)
    ai_bullets = models.JSONField(default=list, blank=True)
    seo_title = models.CharField(max_length=300, blank=True)
    meta_description = models.TextField(blank=True)
    keywords = models.JSONField(default=list, blank=True)
    search_phrases = models.JSONField(default=list, blank=True)
    intelligence_score = models.PositiveIntegerField(null=True, blank=True)
    missing_information = models.JSONField(default=list, blank=True)
    image_quality_score = models.PositiveIntegerField(null=True, blank=True)
    image_quality_suggestions = models.JSONField(default=list, blank=True)
    ai_analysis_raw = models.JSONField(default=dict, blank=True)
    ai_analyzed_at = models.DateTimeField(null=True, blank=True)
    def __str__(self): return self.name
    def get_absolute_url(self): return reverse('product_detail', args=[self.pk])

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    attributes = models.JSONField(default=dict, blank=True)
    image = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    def __str__(self): return f'{self.product.name} - {self.name}'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def total(self): return sum(item.subtotal for item in self.items.select_related('product').all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    class Meta: unique_together = ('cart','product')
    @property
    def subtotal(self): return (self.product.price or 0) * self.quantity

class Order(models.Model):

    STATUS = [
        ("pending", "Order Placed"),
        ("confirmed", "Order Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHODS = [
        ("cod", "Cash on Delivery"),
        ("online", "Online Payment"),
    ]

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    order_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default="pending"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default="cod"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending"
    )

    full_name = models.CharField(
        max_length=150,
        blank=True
    )

    phone = models.CharField(
        max_length=30,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True
    )

    state = models.CharField(
        max_length=100,
        blank=True
    )

    pincode = models.CharField(
        max_length=20,
        blank=True
    )

    tracking_number = models.CharField(
        max_length=100,
        blank=True
    )

    courier_name = models.CharField(
        max_length=100,
        blank=True
    )

    estimated_delivery = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        import uuid

        # Generate order number automatically
        if not self.order_number:
            self.order_number = (
                "VETRI-" +
                uuid.uuid4().hex[:10].upper()
            )

        # Generate tracking number automatically
        if not self.tracking_number:
            self.tracking_number = (
                "TRK-" +
                uuid.uuid4().hex[:12].upper()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.order.order_number} - {self.product.name}"

class OrderTracking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Order Placed"),
        ("confirmed", "Order Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tracking_updates"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES
    )

    description = models.CharField(
        max_length=255
    )

    location = models.CharField(
        max_length=150,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"

class CompetitorProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='competitors')
    competitor_name = models.CharField(max_length=150)
    source_url = models.URLField(blank=True)
    title = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    features = models.JSONField(default=dict, blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    review_text = models.TextField()
    sentiment = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AIContent(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ai_contents')
    content_type = models.CharField(max_length=50)
    content = models.JSONField(default=dict)
    approved = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatConversation(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    session_key = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
