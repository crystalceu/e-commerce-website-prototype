from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("account", views.account, name="account"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("update_watchlist/<int:listing_id>", views.update_watchlist, name="update_watchlist"),
    path("cart", views.cart, name="cart"),
    path("add_comment", views.add_comment, name="add_comment"),
    path("cart/orders", views.orders_view, name="orders_view"),
    path("cart/order/<int:order_id>", views.order_view, name="order_view"),
    path("cart/update_cart/<int:listing_id>/<str:action>", views.update_cart, name="update_cart"),
    path("products/<str:bigcategory>", views.listings, name="categories"),
    path("products/<str:bigcategory>/<str:category>", views.listing, name="category"),
    path("products/<str:bigcategory>/<str:category>/<int:listing_id>", views.listing_view, name="listing_view"),
]