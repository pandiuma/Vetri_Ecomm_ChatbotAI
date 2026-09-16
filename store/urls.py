from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "products/",
        views.products,
        name="products"
    ),

    path(
        "products/<int:pk>/",
        views.product_detail,
        name="product_detail"
    ),

    path(
        "about/",
        views.about,
        name="about"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    path(
        "products/create/",
        views.product_create,
        name="product_create"
    ),

    path(
        "products/<int:pk>/intelligence/",
        views.product_intelligence,
        name="product_intelligence"
    ),

    path(
        "api/subcategories/<int:category_id>/",
        views.subcategories,
        name="subcategories"
    ),

    # CART
    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "cart/add/<int:pk>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/update/<int:item_id>/",
        views.update_cart,
        name="update_cart"
    ),

    path(
        "cart/remove/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    # CHECKOUT
    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    # ORDERS
    path(
        "orders/",
        views.order_history,
        name="order_history"
    ),

    path(
        "orders/<int:pk>/",
        views.order_detail,
        name="order_detail"
    ),

    path(
        "orders/<int:pk>/tracking/",
        views.order_tracking,
        name="order_tracking"
    ),

    # CHATBOT
    path(
        "chatbot/",
        views.chatbot,
        name="chatbot"
    ),

    path(
        "api/chatbot/",
        views.chatbot_api,
        name="chatbot_api"
    ),


    path(
    'password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'
    ),
    name='password_reset'
),

path(
    'password-reset/done/',
    auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ),
    name='password_reset_done'
),

path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ),
    name='password_reset_confirm'
),

path(
    'reset/done/',
    auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ),
    name='password_reset_complete'
),
]
