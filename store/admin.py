from django.contrib import admin

from .models import (
    UserProfile,
    Category,
    SubCategory,
    CategoryAttribute,
    Product,
    ProductImage,
    ProductVariant,
    Cart,
    CartItem,
    Order,
    OrderItem,
    OrderTracking,
    CompetitorProduct,
    ProductReview,
    AIContent,
    AuditLog,
    ChatConversation,
    ChatMessage,
)


# =========================================================
# USER PROFILE
# =========================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "role",
    )

    list_filter = (
        "role",
    )

    search_fields = (
        "user__username",
        "user__email",
    )


# =========================================================
# CATEGORY
# =========================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "description",
    )

    search_fields = (
        "name",
    )


# =========================================================
# SUBCATEGORY
# =========================================================

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
    )

    list_filter = (
        "category",
    )

    search_fields = (
        "name",
        "category__name",
    )


# =========================================================
# CATEGORY ATTRIBUTE
# =========================================================

@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "field_type",
        "required",
    )

    list_filter = (
        "category",
        "field_type",
        "required",
    )

    search_fields = (
        "name",
        "category__name",
    )


# =========================================================
# PRODUCT IMAGE
# =========================================================

class ProductImageInline(admin.TabularInline):

    model = ProductImage

    extra = 1


# =========================================================
# PRODUCT VARIANT
# =========================================================

class ProductVariantInline(admin.TabularInline):

    model = ProductVariant

    extra = 1


# =========================================================
# PRODUCT
# =========================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "brand",
        "category",
        "subcategory",
        "price",
        "inventory",
        "lifecycle",
        "ai_analyzed_at",
    )

    list_filter = (
        "category",
        "subcategory",
        "lifecycle",
        "created_at",
    )

    search_fields = (
        "name",
        "brand",
        "sku",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "ai_analyzed_at",
    )

    inlines = [
        ProductImageInline,
        ProductVariantInline,
    ]


# =========================================================
# CART
# =========================================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )


# =========================================================
# CART ITEM
# =========================================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "cart",
        "product",
        "quantity",
        "subtotal",
    )

    search_fields = (
        "product__name",
        "cart__user__username",
    )


# =========================================================
# ORDER ITEM INLINE
# =========================================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "product",
        "quantity",
        "price",
    )


# =========================================================
# ORDER TRACKING INLINE
# =========================================================

class OrderTrackingInline(admin.TabularInline):

    model = OrderTracking

    extra = 0


# =========================================================
# ORDER
# =========================================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "user",
        "total",
        "status",
        "payment_method",
        "payment_status",
        "tracking_number",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "payment_status",
        "created_at",
    )

    search_fields = (
        "order_number",
        "user__username",
        "user__email",
        "phone",
        "tracking_number",
    )

    readonly_fields = (
        "order_number",
        "created_at",
        "updated_at",
    )

    fieldsets = (

        (
            "Order Information",
            {
                "fields": (
                    "order_number",
                    "user",
                    "total",
                    "status",
                )
            },
        ),

        (
            "Payment",
            {
                "fields": (
                    "payment_method",
                    "payment_status",
                )
            },
        ),

        (
            "Customer Details",
            {
                "fields": (
                    "full_name",
                    "phone",
                    "address",
                    "city",
                    "state",
                    "pincode",
                )
            },
        ),

        (
            "Shipping & Tracking",
            {
                "fields": (
                    "tracking_number",
                    "courier_name",
                    "estimated_delivery",
                )
            },
        ),

        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    inlines = [
        OrderItemInline,
        OrderTrackingInline,
    ]


# =========================================================
# ORDER TRACKING
# =========================================================

@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "status",
        "location",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "location",
        "description",
    )


# =========================================================
# COMPETITOR PRODUCT
# =========================================================

@admin.register(CompetitorProduct)
class CompetitorProductAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "competitor_name",
        "price",
        "captured_at",
    )

    list_filter = (
        "competitor_name",
        "captured_at",
    )

    search_fields = (
        "product__name",
        "competitor_name",
        "title",
    )


# =========================================================
# PRODUCT REVIEW
# =========================================================

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "rating",
        "sentiment",
        "created_at",
    )

    list_filter = (
        "rating",
        "sentiment",
        "created_at",
    )

    search_fields = (
        "product__name",
        "review_text",
    )


# =========================================================
# AI CONTENT
# =========================================================

@admin.register(AIContent)
class AIContentAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "content_type",
        "approved",
        "created_by",
        "created_at",
    )

    list_filter = (
        "content_type",
        "approved",
        "created_at",
    )

    search_fields = (
        "product__name",
        "content_type",
    )


# =========================================================
# AUDIT LOG
# =========================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "action",
        "object_type",
        "object_id",
        "created_at",
    )

    list_filter = (
        "action",
        "object_type",
        "created_at",
    )

    search_fields = (
        "user__username",
        "action",
        "object_type",
        "object_id",
    )


# =========================================================
# CHAT CONVERSATION
# =========================================================

@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "session_key",
        "created_at",
    )

    search_fields = (
        "user__username",
        "session_key",
    )


# =========================================================
# CHAT MESSAGE
# =========================================================

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):

    list_display = (
        "conversation",
        "role",
        "created_at",
    )

    list_filter = (
        "role",
        "created_at",
    )

    search_fields = (
        "content",
    )
