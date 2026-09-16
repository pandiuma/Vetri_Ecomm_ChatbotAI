
import json
import re
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .ai_services import analyze_product, chatbot_answer
from .models import (
    Cart,
    CartItem,
    Category,
    ChatConversation,
    ChatMessage,
    Order,
    OrderItem,
    OrderTracking,
    Product,
    SubCategory,
)


# ============================================================
# HOME
# ============================================================

def home(request):
    products = Product.objects.select_related(
        "category",
        "subcategory"
    ).all().order_by("-created_at")

    categories = Category.objects.all().order_by("name")

    context = {
        "products": products,
        "new_products": products[:8],
        "categories": categories,
    }

    return render(
        request,
        "store/home.html",
        context
    )


# ============================================================
# PRODUCTS
# ============================================================

def products(request):
    product_list = Product.objects.select_related(
        "category",
        "subcategory"
    ).all().order_by("-created_at")

    category_id = request.GET.get("category")

    if category_id:
        product_list = product_list.filter(
            category_id=category_id
        )

    search = request.GET.get("q", "").strip()

    if search:
        product_list = product_list.filter(
            name__icontains=search
        )

    categories = Category.objects.all().order_by("name")

    context = {
        "products": product_list,
        "categories": categories,
        "search": search,
    }

    return render(
        request,
        "store/products.html",
        context
    )


# ============================================================
# PRODUCT DETAIL
# ============================================================

def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related(
            "category",
            "subcategory"
        ).prefetch_related(
            "images",
            "variants",
            "reviews"
        ),
        pk=pk
    )

    related_products = Product.objects.filter(
        category=product.category
    ).exclude(
        pk=product.pk
    )[:4]

    context = {
        "product": product,
        "related_products": related_products,
    }

    return render(
        request,
        "store/product_detail.html",
        context
    )


# ============================================================
# ABOUT
# ============================================================

def about(request):
    return render(
        request,
        "store/about.html"
    )


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("dashboard")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "store/login.html"
    )


# ============================================================
# REGISTER
# ============================================================

def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not username or not password:

            messages.error(
                request,
                "Username and password are required."
            )

            return render(
                request,
                "store/register.html"
            )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "store/register.html"
            )

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(
                request,
                "store/register.html"
            )

        if email and User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return render(
                request,
                "store/register.html"
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(
            request,
            user
        )

        messages.success(
            request,
            "Registration successful."
        )

        return redirect("dashboard")

    return render(
        request,
        "store/register.html"
    )


# ============================================================
# LOGOUT
# ============================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect("home")


# ============================================================
# DASHBOARD
# ============================================================

@login_required
def dashboard(request):

    products_count = Product.objects.count()
    categories_count = Category.objects.count()
    orders_count = Order.objects.count()

    customers_count = User.objects.filter(
        is_staff=False
    ).count()

    role = "Administrator" if request.user.is_staff else "Customer"

    context = {
        "products_count": products_count,
        "categories_count": categories_count,
        "orders_count": orders_count,
        "customers_count": customers_count,
        "role": role,
    }

    return render(
        request,
        "store/dashboard.html",
        context
    )


# ============================================================
# CREATE PRODUCT
# ============================================================

@login_required
def product_create(request):

    categories = Category.objects.all().order_by("name")

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        brand = request.POST.get("brand", "").strip()
        sku = request.POST.get("sku", "").strip()

        price = request.POST.get("price")
        cost = request.POST.get("cost")

        description = request.POST.get(
            "description",
            ""
        ).strip()

        inventory = request.POST.get(
            "inventory",
            "0"
        )

        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")

        image = request.FILES.get("image")

        # Validate product name
        if not name:

            messages.error(
                request,
                "Product name is required."
            )

            return render(
                request,
                "store/product_create.html",
                {
                    "categories": categories,
                    "form_data": request.POST,
                }
            )

        # Convert inventory to integer
        try:
            inventory_value = int(inventory or 0)

        except (ValueError, TypeError):
            inventory_value = 0

        # Create product
        product = Product.objects.create(
            name=name,
            brand=brand,
            sku=sku or None,
            price=price or None,
            cost=cost or None,
            description=description,
            inventory=inventory_value,
            category_id=category_id or None,
            subcategory_id=subcategory_id or None,
            image=image,
            created_by=request.user,
        )

        messages.success(
            request,
            "Product created successfully."
        )

        return redirect(
            "product_detail",
            pk=product.pk
        )

    return render(
        request,
        "store/product_create.html",
        {
            "categories": categories
        }
    )


# ============================================================
# PRODUCT INTELLIGENCE / AI ANALYSIS
# ============================================================

@login_required
def product_intelligence(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    ai_data = None
    analysis_error = None

    # ---------------------------------------------------------
    # RUN AI ANALYSIS
    # ---------------------------------------------------------

    if request.method == "POST":

        result = analyze_product(product)

        if result.get("success"):

            ai_data = result.get(
                "data",
                {}
            )

            field_mapping = {
                "product_type": "ai_product_type",
                "colors": "ai_colors",
                "material": "ai_materials",
                "materials": "ai_materials",
                "style": "ai_style",
                "use_case": "ai_use_case",
            }

            for ai_field, model_field in field_mapping.items():

                if ai_field not in ai_data:
                    continue

                value = ai_data.get(ai_field)

                if isinstance(value, list):
                    value = ", ".join(
                        str(item)
                        for item in value
                    )

                try:
                    Product._meta.get_field(
                        model_field
                    )

                    setattr(
                        product,
                        model_field,
                        value or ""
                    )

                except Exception:
                    pass

            product.save()

            messages.success(
                request,
                "AI product analysis completed successfully."
            )

        else:

            analysis_error = result.get(
                "error",
                "Unable to analyze this product."
            )

            messages.error(
                request,
                f"AI analysis failed: {analysis_error}"
            )

    # ---------------------------------------------------------
    # DISPLAY PREVIOUSLY SAVED AI INFORMATION
    # ---------------------------------------------------------

    if ai_data is None:

        ai_data = {}

        saved_field_mapping = {
            "product_type": "ai_product_type",
            "colors": "ai_colors",
            "material": "ai_materials",
            "style": "ai_style",
            "use_case": "ai_use_case",
        }

        for ai_field, model_field in saved_field_mapping.items():

            try:

                value = getattr(
                    product,
                    model_field,
                    ""
                )

                if value:
                    ai_data[ai_field] = value

            except Exception:
                pass

    return render(
        request,
        "store/product_intelligence.html",
        {
            "product": product,
            "ai_data": ai_data,
            "analysis_error": analysis_error,
        },
    )


# ============================================================
# SUBCATEGORIES API
# ============================================================

def subcategories(request, category_id):

    category = get_object_or_404(
        Category,
        pk=category_id
    )

    subcategories_list = SubCategory.objects.filter(
        category=category
    ).order_by("name")

    data = [
        {
            "id": subcategory.id,
            "name": subcategory.name,
        }
        for subcategory in subcategories_list
    ]

    return JsonResponse(
        {
            "subcategories": data
        }
    )


# ============================================================
# CART
# ============================================================

@login_required
def cart(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    items = cart.items.select_related(
        "product"
    ).all()

    context = {
        "cart": cart,
        "items": items,
        "total": cart.total,
    }

    return render(
        request,
        "store/cart.html",
        context
    )


# ============================================================
# ADD TO CART
# ============================================================

@login_required
def add_to_cart(request, pk):

    product = get_object_or_404(
        Product,
        pk=pk
    )

    if product.inventory <= 0:

        messages.error(
            request,
            "This product is currently out of stock."
        )

        # If request came from Product Intelligence page,
        # stay on the same page.
        if request.GET.get("from_intelligence") == "1":
            return redirect(
                "product_intelligence",
                pk=product.pk
            )

        return redirect(
            "product_detail",
            pk=product.pk
        )

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not item_created:

        if item.quantity < product.inventory:

            item.quantity += 1
            item.save()

        else:

            messages.warning(
                request,
                "You cannot add more than the available stock."
            )

            if request.GET.get("from_intelligence") == "1":
                return redirect(
                    "product_intelligence",
                    pk=product.pk
                )

            return redirect("cart")

    messages.success(
        request,
        f"{product.name} added to your cart."
    )

    # Stay on Product Intelligence page
    if request.GET.get("from_intelligence") == "1":
        return redirect(
            "product_intelligence",
            pk=product.pk
        )

    # Existing behaviour remains unchanged
    return redirect("cart")


# ============================================================
# REMOVE FROM CART
# ============================================================

@login_required
def remove_from_cart(request, item_id):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart=cart
    )

    product_name = item.product.name

    item.delete()

    messages.success(
        request,
        f"{product_name} removed from your cart."
    )

    return redirect("cart")


# ============================================================
# UPDATE CART
# ============================================================

@login_required
def update_cart(request, item_id):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required."
        }, status=405)

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    item = get_object_or_404(
        CartItem.objects.select_related("product"),
        pk=item_id,
        cart=cart
    )

    try:
        quantity = int(
            request.POST.get("quantity", item.quantity)
        )
    except (ValueError, TypeError):
        quantity = item.quantity

    # -----------------------------------------
    # QUANTITY LESS THAN 1
    # -----------------------------------------

    if quantity < 1:
        quantity = 1

    # -----------------------------------------
    # CHECK INVENTORY
    # -----------------------------------------

    if quantity > item.product.inventory:

        quantity = item.product.inventory

        if quantity <= 0:

            item.delete()

            return JsonResponse({
                "success": True,
                "deleted": True,
                "message": "Product is out of stock.",
                "cart_total": float(cart.total),
            })

    # -----------------------------------------
    # SAVE QUANTITY
    # -----------------------------------------

    item.quantity = quantity
    item.save()

    # Refresh cart total
    cart.refresh_from_db()

    # -----------------------------------------
    # CALCULATE SUBTOTAL
    # -----------------------------------------

    subtotal = item.product.price * item.quantity

    return JsonResponse({
        "success": True,
        "deleted": False,
        "quantity": item.quantity,
        "subtotal": float(subtotal),
        "cart_total": float(cart.total),
        "inventory": item.product.inventory,
    })


# ============================================================
# ORDER DETAIL
# ============================================================

@login_required
def order_detail(request, pk):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__product",
            "tracking_updates"
        ),
        pk=pk,
        user=request.user
    )

    return render(
        request,
        "store/order_detail.html",
        {
            "order": order
        }
    )


# ============================================================
# ORDER TRACKING
# ============================================================

@login_required
def order_tracking(request, pk):

    order = get_object_or_404(
        Order,
        pk=pk,
        user=request.user
    )

    tracking = order.tracking_updates.order_by(
        "created_at"
    )

    return render(
        request,
        "store/order_tracking.html",
        {
            "order": order,
            "tracking": tracking,
            "current_status": order.get_status_display(),
            "tracking_number": order.tracking_number,
            "courier_name": order.courier_name,
            "estimated_delivery": order.estimated_delivery,
        }
    )


# ============================================================
# CHECKOUT
# ============================================================

@login_required
def checkout(request):

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    items = list(
        cart.items.select_related(
            "product"
        ).all()
    )

    if not items:

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    for item in items:

        if item.quantity > item.product.inventory:

            messages.error(
                request,
                f"Not enough stock available for "
                f"{item.product.name}."
            )

            return redirect("cart")

    total = cart.total

    if request.method == "POST":

        full_name = request.POST.get(
            "full_name",
            ""
        ).strip()

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        address = request.POST.get(
            "address",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        state = request.POST.get(
            "state",
            ""
        ).strip()

        pincode = request.POST.get(
            "pincode",
            ""
        ).strip()

        payment_method = request.POST.get(
            "payment_method",
            "cod"
        )

        if not full_name:

            messages.error(
                request,
                "Please enter your full name."
            )

            return redirect("checkout")

        if not phone:

            messages.error(
                request,
                "Please enter your phone number."
            )

            return redirect("checkout")

        if not address:

            messages.error(
                request,
                "Please enter your delivery address."
            )

            return redirect("checkout")

        if not city or not state or not pincode:

            messages.error(
                request,
                "Please complete your address."
            )

            return redirect("checkout")

        if payment_method not in [
            "cod",
            "online"
        ]:

            payment_method = "cod"

        payment_status = (
            "paid"
            if payment_method == "online"
            else "pending"
        )

        order = Order.objects.create(
            user=request.user,
            total=total,
            status="pending",
            payment_method=payment_method,
            payment_status=payment_status,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
        )

        for item in items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price or 0
            )

            item.product.inventory -= item.quantity

            if item.product.inventory == 0:

                item.product.lifecycle = "out"

            item.product.save(
                update_fields=[
                    "inventory",
                    "lifecycle",
                    "updated_at"
                ]
            )

        OrderTracking.objects.create(
            order=order,
            status="pending",
            description=(
                "Your order has been placed successfully."
            ),
            location=city
        )

        cart.items.all().delete()

        messages.success(
            request,
            f"Order {order.order_number} placed successfully!"
        )

        return redirect(
            "order_detail",
            pk=order.pk
        )

    context = {
        "cart": cart,
        "items": items,
        "total": total,
    }

    return render(
        request,
        "store/checkout.html",
        context
    )


# ============================================================
# ORDER HISTORY
# ============================================================

@login_required
def order_history(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "store/order_history.html",
        {
            "orders": orders
        }
    )


# ============================================================
# AI CHATBOT PAGE
# ============================================================

def chatbot(request):

    return render(
        request,
        "store/chatbot.html"
    )


# ============================================================
# AI CHATBOT API
# ============================================================

@csrf_exempt
def chatbot_api(request):

    # ============================================================
    # 1. REQUEST VALIDATION
    # ============================================================

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "answer": "Invalid request method.",
            "products": [],
        })

    try:
        body = json.loads(request.body or "{}")
    except Exception:
        return JsonResponse({
            "success": False,
            "answer": "Invalid request data.",
            "products": [],
        })

    question = str(body.get("question", "")).strip()

    if not question:
        return JsonResponse({
            "success": True,
            "answer": "Please enter your question.",
            "products": [],
        })

    normalized_question = question.lower().strip()

    clean_question = re.sub(
        r"[^\w\s₹]",
        " ",
        normalized_question
    )

    clean_question = re.sub(
        r"\s+",
        " ",
        clean_question
    ).strip()

    # ============================================================
    # 2. LOAD PRODUCTS
    # ============================================================

    products = (
        Product.objects
        .select_related("category", "subcategory")
        .all()
        .order_by("-id")[:100]
    )

    product_data = []

    for product in products:

        image_url = ""

        if product.image:
            try:
                image_url = product.image.url
            except Exception:
                image_url = ""

        product_data.append({
            "id": product.id,
            "name": product.name,
            "brand": product.brand or "",
            "sku": product.sku or "",
            "price": float(product.price or 0),
            "cost": float(product.cost or 0),

            "image": image_url,
            "image_url": image_url,
            "chatbot_image_url": image_url,

            "inventory": int(product.inventory or 0),
            "lifecycle": product.lifecycle or "",

            "category": (
                product.category.name
                if product.category
                else ""
            ),

            "subcategory": (
                product.subcategory.name
                if product.subcategory
                else ""
            ),

            "description": product.description or "",

            "ai_product_type": product.ai_product_type or "",
            "ai_category": product.ai_category or "",
            "ai_subcategory": product.ai_subcategory or "",
            "ai_colors": product.ai_colors or [],
            "ai_materials": product.ai_materials or [],
            "ai_style": product.ai_style or "",
            "ai_use_case": product.ai_use_case or "",
            "ai_confidence": product.ai_confidence,
            "ai_attributes": product.ai_attributes or {},
            "keywords": product.keywords or [],
            "search_phrases": product.search_phrases or [],
        })

    # ============================================================
    # 3. PRODUCT CARD
    # ============================================================

    def make_product_card(product):

        return {
            "id": product.get("id"),

            "name": product.get("name", ""),

            "brand": product.get("brand", ""),

            "price": product.get("price", 0),

            "inventory": product.get("inventory", 0),

            "image": product.get("image", ""),

            "image_url": product.get(
                "image_url",
                ""
            ),

            "chatbot_image_url": product.get(
                "chatbot_image_url",
                ""
            ),

            # ADD TO CART LINK
            "cart_url": (
                f"/cart/add/{product.get('id')}/"
            ),

            # PRODUCT DETAILS LINK
            "product_url": (
                f"/products/{product.get('id')}/"
            ),
        }

    # ============================================================
    # 4. GREETING
    # ============================================================

    greeting_words = [
        "hi",
        "hello",
        "hey",
        "hai",
        "good morning",
        "good afternoon",
        "good evening",
    ]

    if clean_question in greeting_words:

        return JsonResponse({
            "success": True,
            "answer": (
                "Hello! 👋 Welcome to **Vetri AI**.\n\n"
                "I can help you with:\n"
                "• Product details\n"
                "• Product comparison\n"
                "• Recommendations\n"
                "• Cart details\n"
                "• Add products to cart\n"
                "• Order details\n"
                "• Tracking details"
            ),
            "products": [],
        })

    # ============================================================
    # 5. EXPLICIT PRODUCT NAME MATCHING
    # ============================================================

    exact_products = []

    for product in product_data:

        product_name = (
            product.get("name", "")
            or ""
        ).lower().strip()

        if not product_name:
            continue

        if product_name in clean_question:

            if product not in exact_products:
                exact_products.append(product)

    # ============================================================
    # 6. COMPARISON QUESTION
    # ============================================================

    comparison_words = [
        "compare",
        "comparison",
        "difference",
        "versus",
        "vs",
        "vs.",
    ]

    comparison_question = any(
        word in clean_question
        for word in comparison_words
    )

    comparison_context_words = [
        "which",
        "best",
        "better",
        "preferred",
        "choice",
        "should i buy",
        "which one",
    ]

    comparison_with_context = (
        len(exact_products) >= 2
        and any(
            word in clean_question
            for word in comparison_context_words
        )
    )

    if comparison_question or comparison_with_context:

        if len(exact_products) < 2:

            return JsonResponse({
                "success": True,
                "answer": (
                    "I can compare two products for you. "
                    "Please mention both product names clearly.\n\n"
                    "Example:\n"
                    "**Compare Pink Shoulder Handbag "
                    "and Classic Grey Leather Handbag.**"
                ),
                "products": [],
            })

        first = exact_products[0]
        second = exact_products[1]

        first_price = float(
            first.get("price") or 0
        )

        second_price = float(
            second.get("price") or 0
        )

        first_stock = int(
            first.get("inventory") or 0
        )

        second_stock = int(
            second.get("inventory") or 0
        )

        # --------------------------------------------------------
        # COMPARISON SCORE
        # --------------------------------------------------------

        first_score = 0
        second_score = 0

        # Lower price
        if first_price < second_price:
            first_score += 2

        elif second_price < first_price:
            second_score += 2

        # Better stock
        if first_stock > second_stock:
            first_score += 1

        elif second_stock > first_stock:
            second_score += 1

        # Available
        if first_stock > 0:
            first_score += 2

        if second_stock > 0:
            second_score += 2

        # Product quality information
        quality_words = [
            "premium",
            "quality",
            "durable",
            "elegant",
            "stylish",
            "comfortable",
            "professional",
            "leather",
            "classic",
        ]

        first_text = " ".join([
            str(first.get("description", "")),
            str(first.get("ai_style", "")),
            str(first.get("ai_use_case", "")),
            str(first.get("ai_materials", "")),
        ]).lower()

        second_text = " ".join([
            str(second.get("description", "")),
            str(second.get("ai_style", "")),
            str(second.get("ai_use_case", "")),
            str(second.get("ai_materials", "")),
        ]).lower()

        for word in quality_words:

            if word in first_text:
                first_score += 1

            if word in second_text:
                second_score += 1

        # --------------------------------------------------------
        # WINNER
        # --------------------------------------------------------

        if first_score > second_score:

            winner = first
            loser = second

        elif second_score > first_score:

            winner = second
            loser = first

        else:

            if first_price <= second_price:
                winner = first
                loser = second
            else:
                winner = second
                loser = first

        # --------------------------------------------------------
        # COMPARISON ANSWER
        # --------------------------------------------------------

        comparison_answer = (
            "### 🛍️ Product Comparison\n\n"

            f"**1. {first.get('name')}**\n"
            f"- Brand: {first.get('brand') or 'N/A'}\n"
            f"- Price: ₹{first_price:,.2f}\n"
            f"- Stock: {first_stock} units\n"
            f"- Category: "
            f"{first.get('category') or 'N/A'}\n"
            f"- Subcategory: "
            f"{first.get('subcategory') or 'N/A'}\n"
        )

        if first.get("description"):

            comparison_answer += (
                f"- Description: "
                f"{first.get('description')}\n"
            )

        comparison_answer += "\n"

        comparison_answer += (
            f"**2. {second.get('name')}**\n"
            f"- Brand: {second.get('brand') or 'N/A'}\n"
            f"- Price: ₹{second_price:,.2f}\n"
            f"- Stock: {second_stock} units\n"
            f"- Category: "
            f"{second.get('category') or 'N/A'}\n"
            f"- Subcategory: "
            f"{second.get('subcategory') or 'N/A'}\n"
        )

        if second.get("description"):

            comparison_answer += (
                f"- Description: "
                f"{second.get('description')}\n"
            )

        comparison_answer += "\n"

        comparison_answer += (
            "### 🏆 Better Choice\n\n"

            f"**{winner.get('name')}** is the better "
            "choice based on price, availability and "
            "product information in the current catalog.\n\n"
        )

        if winner.get("price", 0) < loser.get("price", 0):

            comparison_answer += (
                f"💰 It is more affordable at "
                f"₹{float(winner.get('price') or 0):,.2f}, "
                f"compared with "
                f"₹{float(loser.get('price') or 0):,.2f} "
                f"for {loser.get('name')}.\n\n"
            )

        if (
            winner.get("inventory", 0)
            >
            loser.get("inventory", 0)
        ):

            comparison_answer += (
                f"📦 It also has better availability "
                f"with {winner.get('inventory')} "
                "units in stock.\n\n"
            )

        if winner.get("description"):

            comparison_answer += (
                f"⭐ **Why:** "
                f"{winner.get('description')}\n\n"
            )

        comparison_answer += (
            "You can use the **Add to Cart** button "
            "on the product card to purchase your choice."
        )

        return JsonResponse({

            "success": True,

            "answer": comparison_answer,

            "products": [
                make_product_card(first),
                make_product_card(second),
            ],

            "winner": make_product_card(winner),

            "cart_url": "/cart/",
        })

    # ============================================================
    # 7. HOW TO ADD PRODUCT TO CART
    # ============================================================

    how_to_cart_phrases = [

        "how can add products to my cart",
        "how can i add products to my cart",
        "how do i add products to my cart",
        "how to add products to my cart",

        "how to add product to cart",
        "how can i add product to cart",
        "how do i add product to cart",

        "add products to my cart",
        "add product to my cart",

        "how can i add items to cart",
        "how do i add items to cart",
        "how to add items to cart",

        "how can i add something to cart",
        "how do i add something to cart",
    ]

    if any(
        phrase in clean_question
        for phrase in how_to_cart_phrases
    ):

        return JsonResponse({

            "success": True,

            "answer": (
                "🛒 **How to Add a Product to Your Cart**\n\n"

                "1. Search for the product you want.\n"
                "2. Open the product details.\n"
                "3. Click **Add to Cart**.\n"
                "4. The product will be added to your cart.\n"
                "5. You can open your cart using the "
                "**Cart** button.\n\n"

                "You can also ask me:\n"
                "**Add Pink Shoulder Handbag to my cart**"
            ),

            "products": [],
        })

    # ============================================================
    # 8. ADD PRODUCT TO CART
    # ============================================================

    add_words = [
        "add",
        "buy",
        "purchase",
        "put",
        "include",
    ]

    cart_words = [
        "cart",
        "basket",
    ]

    is_add_to_cart = (
        any(word in clean_question for word in add_words)
        and
        any(word in clean_question for word in cart_words)
    )

    if is_add_to_cart:

        if not request.user.is_authenticated:

            return JsonResponse({

                "success": True,

                "answer": (
                    "Please log in before adding products "
                    "to your cart."
                ),

                "products": [],

                "login_url": "/login/",
            })

        matched_product = None

        # Exact product match first
        for product in product_data:

            product_name = (
                product.get("name", "")
                or ""
            ).lower().strip()

            if (
                product_name
                and product_name in clean_question
            ):

                matched_product = product
                break

        # Token-based fallback
        if not matched_product:

            best_score = 0

            question_words = set(
                clean_question.split()
            )

            for product in product_data:

                product_name = (
                    product.get("name", "")
                    or ""
                ).lower()

                product_words = set(
                    product_name.split()
                )

                score = len(
                    question_words
                    &
                    product_words
                )

                if score > best_score:

                    best_score = score
                    matched_product = product

        if not matched_product:

            return JsonResponse({

                "success": True,

                "answer": (
                    "Please mention the product name "
                    "you want to add to your cart."
                ),

                "products": [],
            })

        inventory = int(
            matched_product.get("inventory") or 0
        )

        if inventory <= 0:

            return JsonResponse({

                "success": True,

                "answer": (
                    f"Sorry, **{matched_product.get('name')}** "
                    "is currently out of stock."
                ),

                "products": [
                    make_product_card(matched_product)
                ],
            })

        user_cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_item, created = CartItem.objects.get_or_create(

            cart=user_cart,

            product_id=matched_product.get("id"),

            defaults={
                "quantity": 1
            }
        )

        if not created:

            if cart_item.quantity < inventory:

                cart_item.quantity += 1
                cart_item.save()

            else:

                return JsonResponse({

                    "success": True,

                    "answer": (
                        f"You already have the maximum "
                        f"available quantity of "
                        f"**{matched_product.get('name')}** "
                        "in your cart."
                    ),

                    "products": [
                        make_product_card(
                            matched_product
                        )
                    ],

                    "cart_url": "/cart/",
                })

        return JsonResponse({

            "success": True,

            "answer": (
                f"🛒 **{matched_product.get('name')}** "
                "has been added to your cart successfully.\n\n"
                "You can continue shopping or open your cart."
            ),

            "products": [
                make_product_card(
                    matched_product
                )
            ],

            "cart_url": "/cart/",
        })

    # ============================================================
    # 9. GET USER CART DATA
    # ============================================================

    cart_data = []

    if request.user.is_authenticated:

        user_cart = Cart.objects.filter(
            user=request.user
        ).first()

        if user_cart:

            cart_items = (
                CartItem.objects
                .filter(cart=user_cart)
                .select_related("product")
            )

            for item in cart_items:

                cart_data.append({

                    "id": item.product.id,

                    "name": item.product.name,

                    "brand": item.product.brand or "",

                    "quantity": item.quantity,

                    "price": float(
                        item.product.price or 0
                    ),

                    "subtotal": float(
                        item.subtotal or 0
                    ),

                    "inventory": int(
                        item.product.inventory or 0
                    ),
                })

    # ============================================================
    # 10. TRACKING DETAILS
    # ============================================================

    tracking_phrases = [

        "track my order",
        "track order",

        "tracking details",
        "tracking detail",

        "my tracking details",
        "provide my tracking details",
        "show my tracking details",
        "get my tracking details",

        "order tracking",

        "where is my order",
        "where is my package",
        "where is my parcel",

        "delivery status",
        "delivery update",

        "tracking number",

        "track my package",
        "track my parcel",

        "my tracking orders",
        "my delivery",
        "delivery details",
    ]

    if any(
        phrase in clean_question
        for phrase in tracking_phrases
    ):

        if not request.user.is_authenticated:

            return JsonResponse({

                "success": True,

                "answer": (
                    "Please log in to view your "
                    "tracking details."
                ),

                "products": [],

                "login_url": "/login/",
            })

        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related(
                "items__product",
                "tracking_updates"
            )
            .order_by("-created_at")[:20]
        )

        order_data = []

        for order in orders:

            tracking_updates = []

            for update in order.tracking_updates.all():

                tracking_updates.append({

                    "status": update.status,

                    "status_display": (
                        update.get_status_display()
                    ),

                    "description": (
                        update.description or ""
                    ),

                    "location": (
                        update.location or ""
                    ),

                    "created_at": (
                        update.created_at.strftime(
                            "%d-%m-%Y %I:%M %p"
                        )
                        if update.created_at
                        else ""
                    ),
                })

            order_data.append({

                "id": order.id,

                "order_number": order.order_number,

                "status": order.status,

                "status_display": (
                    order.get_status_display()
                ),

                "total": float(
                    order.total or 0
                ),

                "payment_method": (
                    order.payment_method
                ),

                "payment_status": (
                    order.payment_status
                ),

                "tracking_number": (
                    order.tracking_number or ""
                ),

                "courier_name": (
                    order.courier_name or ""
                ),

                "estimated_delivery": order.estimated_delivery.strftime(
                    "%d-%m-%Y"
                )
                if order.estimated_delivery
                else "",

                "tracking_updates": tracking_updates,
            })

        if not order_data:

            return JsonResponse({

                "success": True,

                "answer": (
                    "You don't have any orders yet, "
                    "so there are no tracking details "
                    "available."
                ),

                "products": [],
            })

        tracking_answer = (
            "📦 **Your Order Tracking Details**\n\n"
        )

        for order in order_data:

            tracking_answer += (

                f"### Order "
                f"{order.get('order_number')}\n"

                f"**Status:** "
                f"{order.get('status_display')}\n"
            )

            if order.get("tracking_number"):

                tracking_answer += (
                    f"**Tracking Number:** "
                    f"{order.get('tracking_number')}\n"
                )

            if order.get("courier_name"):

                tracking_answer += (
                    f"**Courier:** "
                    f"{order.get('courier_name')}\n"
                )

            if order.get("estimated_delivery"):

                tracking_answer += (
                    f"**Estimated Delivery:** "
                    f"{order.get('estimated_delivery')}\n"
                )

            if order.get("tracking_updates"):

                tracking_answer += (
                    "\n**Tracking Updates:**\n"
                )

                for update in order[
                    "tracking_updates"
                ]:

                    tracking_answer += (
                        f"• **{update.get('status_display')}**"
                    )

                    if update.get("description"):

                        tracking_answer += (
                            f" — "
                            f"{update.get('description')}"
                        )

                    if update.get("location"):

                        tracking_answer += (
                            f" | "
                            f"{update.get('location')}"
                        )

                    if update.get("created_at"):

                        tracking_answer += (
                            f"\n  "
                            f"{update.get('created_at')}"
                        )

                    tracking_answer += "\n"

            tracking_answer += "\n"

        return JsonResponse({

            "success": True,

            "answer": tracking_answer,

            "products": [],

            "orders": order_data,
        })

    # ============================================================
    # 11. CART DETAILS
    # ============================================================

    cart_phrases = [

        "my cart",
        "cart items",
        "items in cart",

        "what is in my cart",
        "what's in my cart",

        "show my cart",
        "show cart",

        "cart total",
        "cart details",

        "my basket",
        "basket items",
    ]

    if any(
        phrase in clean_question
        for phrase in cart_phrases
    ):

        if not request.user.is_authenticated:

            return JsonResponse({

                "success": True,

                "answer": (
                    "Please log in to view your cart."
                ),

                "products": [],

                "login_url": "/login/",
            })

        if not cart_data:

            return JsonResponse({

                "success": True,

                "answer": (
                    "🛒 Your cart is currently empty.\n\n"
                    "You can ask me about a product "
                    "and add it to your cart."
                ),

                "products": [],

                "cart_url": "/cart/",
            })

        cart_answer = (
            "🛒 **Your Cart Details**\n\n"
        )

        cart_total = 0

        for item in cart_data:

            subtotal = float(
                item.get("subtotal") or 0
            )

            cart_total += subtotal

            cart_answer += (

                f"**{item.get('name')}**\n"

                f"- Brand: "
                f"{item.get('brand') or 'N/A'}\n"

                f"- Quantity: "
                f"{item.get('quantity')}\n"

                f"- Price: "
                f"₹{item.get('price', 0):,.2f}\n"

                f"- Subtotal: "
                f"₹{subtotal:,.2f}\n\n"
            )

        cart_answer += (
            f"### 💰 Cart Total: "
            f"₹{cart_total:,.2f}\n\n"

            "You can open your cart using "
            "the **View Cart** button."
        )

        return JsonResponse({

            "success": True,

            "answer": cart_answer,

            "products": [],

            "cart": cart_data,

            "cart_url": "/cart/",
        })

    # ============================================================
    # 12. GET USER ORDER DATA
    # ============================================================

    order_data = []

    if request.user.is_authenticated:

        orders = (
            Order.objects
            .filter(user=request.user)
            .prefetch_related(
                "items__product",
                "tracking_updates"
            )
            .order_by("-created_at")[:20]
        )

        for order in orders:

            order_items = []

            for item in order.items.all():

                order_items.append({

                    "product_id": item.product.id,

                    "product_name": (
                        item.product.name
                    ),

                    "quantity": item.quantity,

                    "price": float(
                        item.price or 0
                    ),

                    "subtotal": float(
                        (item.price or 0)
                        *
                        item.quantity
                    ),
                })

            order_data.append({

                "id": order.id,

                "order_number": (
                    order.order_number
                ),

                "total": float(
                    order.total or 0
                ),

                "status": order.status,

                "status_display": (
                    order.get_status_display()
                ),

                "payment_method": (
                    order.payment_method
                ),

                "payment_status": (
                    order.payment_status
                ),

                "tracking_number": (
                    order.tracking_number or ""
                ),

                "courier_name": (
                    order.courier_name or ""
                ),

                "estimated_delivery": (
                    order.estimated_delivery.strftime(
                        "%d-%m-%Y"
                    )
                    if order.estimated_delivery
                    else ""
                ),

                "created_at": (
                    order.created_at.strftime(
                        "%d-%m-%Y %I:%M %p"
                    )
                    if order.created_at
                    else ""
                ),

                "items": order_items,
            })

    # ============================================================
    # 13. ORDER DETAILS
    # ============================================================

    order_phrases = [

        "my orders",
        "my order",
        "order details",
        "order detail",

        "show my orders",
        "show my order",

        "order history",
        "purchase history",

        "what did i order",
        "what have i ordered",

        "recent orders",
    ]

    if any(
        phrase in clean_question
        for phrase in order_phrases
    ):

        if not request.user.is_authenticated:

            return JsonResponse({

                "success": True,

                "answer": (
                    "Please log in to view your "
                    "order details."
                ),

                "products": [],

                "login_url": "/login/",
            })

        if not order_data:

            return JsonResponse({

                "success": True,

                "answer": (
                    "You don't have any orders yet."
                ),

                "products": [],
            })

        order_answer = (
            "📦 **Your Order Details**\n\n"
        )

        for order in order_data:

            order_answer += (

                f"### Order "
                f"{order.get('order_number')}\n"

                f"**Status:** "
                f"{order.get('status_display')}\n"

                f"**Total:** "
                f"₹{order.get('total', 0):,.2f}\n"

                f"**Payment:** "
                f"{order.get('payment_status')}\n\n"

                "**Products:**\n"
            )

            for item in order.get(
                "items",
                []
            ):

                order_answer += (

                    f"• {item.get('product_name')} "
                    f"x {item.get('quantity')} "
                    f"— ₹{item.get('subtotal', 0):,.2f}\n"
                )

            order_answer += "\n"

        return JsonResponse({

            "success": True,

            "answer": order_answer,

            "products": [],

            "orders": order_data,
        })

    # ============================================================
    # 14. PRODUCT INFORMATION
    # ============================================================

    if len(exact_products) == 1:

        product = exact_products[0]

        product_answer = (
            f"### 🛍️ {product.get('name')}\n\n"

            f"**Brand:** "
            f"{product.get('brand') or 'N/A'}\n\n"

            f"**Price:** "
            f"₹{float(product.get('price') or 0):,.2f}\n\n"

            f"**Availability:** "
            f"{product.get('inventory', 0)} units\n\n"

            f"**Category:** "
            f"{product.get('category') or 'N/A'}\n\n"

            f"**Subcategory:** "
            f"{product.get('subcategory') or 'N/A'}\n\n"
        )

        if product.get("description"):

            product_answer += (
                f"**Description:** "
                f"{product.get('description')}\n\n"
            )

        product_answer += (
            "You can view the product and "
            "add it to your cart using the "
            "product card below."
        )

        return JsonResponse({

            "success": True,

            "answer": product_answer,

            "products": [
                make_product_card(product)
            ],

            "cart_url": (
                f"/cart/add/{product.get('id')}/"
            ),

            "product_url": (
                f"/products/{product.get('id')}/"
            ),
        })

    # ============================================================
    # 15. RECOMMENDATION
    # ============================================================

    recommendation_words = [

        "better",
        "best",
        "recommend",
        "suggest",
        "suitable",
        "ideal",

        "should i buy",
        "what should i buy",

        "good choice",
    ]

    shopping_type_words = [

        "product",
        "bag",
        "handbag",
        "backpack",
        "clutch",
        "shoe",
        "footwear",
        "phone",
        "mobile",
        "keyboard",
    ]

    is_recommendation = (

        any(
            word in clean_question
            for word in recommendation_words
        )

        and

        any(
            word in clean_question
            for word in shopping_type_words
        )
    )

    # IMPORTANT:
    # This section comes AFTER comparison.
    # Therefore:
    # "which handbag is best, A and B"
    # is already handled above.

    if is_recommendation:

        recommendation_products = []

        for product in product_data:

            search_text = " ".join([

                str(product.get("name", "")),

                str(product.get("brand", "")),

                str(product.get("category", "")),

                str(product.get("subcategory", "")),

                str(product.get("description", "")),

                str(product.get("ai_product_type", "")),

                str(product.get("ai_style", "")),

                str(product.get("ai_use_case", "")),

                str(product.get("ai_materials", "")),

            ]).lower()

            score = 0

            question_words = set(
                clean_question.split()
            )

            search_words = set(
                search_text.split()
            )

            score += len(
                question_words
                &
                search_words
            )

            if product.get("inventory", 0) > 0:

                score += 2

            recommendation_products.append(
                (
                    score,
                    product
                )
            )

        recommendation_products.sort(
            key=lambda x: x[0],
            reverse=True
        )

        top_products = [

            item[1]

            for item in recommendation_products[:3]

        ]

        if top_products:

            recommendation_answer = (
                "### ⭐ Recommended Products\n\n"
            )

            for product in top_products:

                recommendation_answer += (

                    f"**{product.get('name')}**\n"

                    f"- Brand: "
                    f"{product.get('brand') or 'N/A'}\n"

                    f"- Price: "
                    f"₹{float(product.get('price') or 0):,.2f}\n"

                    f"- Stock: "
                    f"{product.get('inventory', 0)} units\n\n"
                )

            recommendation_answer += (
                "You can use the **Add to Cart** "
                "button on the product cards."
            )

            return JsonResponse({

                "success": True,

                "answer": recommendation_answer,

                "products": [
                    make_product_card(product)
                    for product in top_products
                ],

                "cart_url": "/cart/",
            })

    # ============================================================
    # 16. AVAILABLE PRODUCTS
    # ============================================================

    available_product_phrases = [
        "available products",
        "available product",
        "products available",
        "product available",
        "show available products",
        "show available product",
        "list available products",
        "list available product",
        "what products are available",
        "what product are available",
        "what products do you have",
        "what product do you have",
        "show me products",
        "show products",
        "list products",
    ]

    is_available_products = any(
        phrase in clean_question
        for phrase in available_product_phrases
    )

    if is_available_products:

        # --------------------------------------------------------
        # CHECK WHETHER USER REQUESTED A PRODUCT CATEGORY
        # --------------------------------------------------------

        category_products = []

        category_keywords = [
            "handbag",
            "handbags",
            "bag",
            "bags",
            "backpack",
            "backpacks",
            "clutch",
            "clutches",
            "shoe",
            "shoes",
            "footwear",
            "phone",
            "phones",
            "mobile",
            "keyboard",
            "keyboards",
            "electronics",
        ]

        requested_category = None

        for keyword in category_keywords:

            if keyword in clean_question:

                requested_category = keyword
                break

        # --------------------------------------------------------
        # FIND AVAILABLE PRODUCTS
        # --------------------------------------------------------

        for product in product_data:

            inventory = int(
                product.get("inventory") or 0
            )

            # Only products currently in stock
            if inventory <= 0:
                continue

            # ----------------------------------------------------
            # CATEGORY FILTER
            # ----------------------------------------------------

            if requested_category:

                product_text = " ".join([

                    str(product.get("name", "")),

                    str(product.get("category", "")),

                    str(product.get("subcategory", "")),

                    str(product.get("description", "")),

                    str(product.get("ai_product_type", "")),

                    str(product.get("ai_category", "")),

                    str(product.get("ai_subcategory", "")),

                    str(product.get("keywords", "")),

                    str(product.get("search_phrases", "")),

                ]).lower()

                # Special handling for bags / handbags
                if requested_category in [
                    "handbag",
                    "handbags",
                ]:

                    handbag_words = [
                        "handbag",
                        "handbags",
                        "purse",
                        "shoulder bag",
                        "leather bag",
                        "women bag",
                    ]

                    if not any(
                        word in product_text
                        for word in handbag_words
                    ):
                        continue

                # General category matching
                elif requested_category not in product_text:

                    continue

            category_products.append(product)

        # --------------------------------------------------------
        # RESPONSE
        # --------------------------------------------------------

        if category_products:

            available_answer = (
                "### 🛍️ Available Products\n\n"
            )

            if requested_category in [
                "handbag",
                "handbags",
            ]:

                available_answer = (
                    "### 👜 Available Handbags\n\n"
                )

            for product in category_products:

                available_answer += (

                    f"**{product.get('name')}**\n"

                    f"- Brand: "
                    f"{product.get('brand') or 'N/A'}\n"

                    f"- Price: "
                    f"₹{float(product.get('price') or 0):,.2f}\n"

                    f"- Stock: "
                    f"{product.get('inventory', 0)} available\n\n"
                )

            available_answer += (
                "You can view the product details or "
                "use the **Add to Cart** button on "
                "the product cards."
            )

            return JsonResponse({

                "success": True,

                "answer": available_answer,

                "products": [
                    make_product_card(product)
                    for product in category_products
                ],

                "cart_url": "/cart/",
            })

        # No matching available products
        return JsonResponse({

            "success": True,

            "answer": (
                "Sorry, there are currently no "
                "available products matching your request."
            ),

            "products": [],
        })

    # ============================================================
    # 17. GEMINI FALLBACK
    # ============================================================

    try:

        answer = chatbot_answer(
            question,
            product_data
        )

        if not answer:

            raise Exception(
                "Empty AI response"
            )

        # --------------------------------------------------------
        # FIND PRODUCTS MENTIONED IN QUESTION / ANSWER
        # --------------------------------------------------------

        response_products = []

        search_text = (
            f"{question} {answer}"
        ).lower()

        for product in product_data:

            product_name = (
                product.get(
                    "name",
                    ""
                )
                or ""
            ).lower()

            brand = (
                product.get(
                    "brand",
                    ""
                )
                or ""
            ).lower()

            if (
                product_name
                and product_name in search_text
            ):

                if product not in response_products:

                    response_products.append(
                        product
                    )

                continue

            if (
                brand
                and brand in search_text
                and product not in response_products
            ):

                response_products.append(product)

        # --------------------------------------------------------
        # RETURN GEMINI RESPONSE
        # --------------------------------------------------------

        return JsonResponse({

            "success": True,

            "answer": answer,

            "products": [

                make_product_card(product)

                for product in response_products[:5]

            ],
        })

    except Exception as e:

        print(
            "Chatbot Error:",
            str(e)
        )

        return JsonResponse({

            "success": False,

            "answer": (
                "Vetri AI could not process "
                "your request."
            ),

            "products": [],
        })


