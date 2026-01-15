from django.urls import path
from . import views

app_name = "films"

urlpatterns = [
    path("", views.index, name="index"),
    path("film/<slug:slug>/", views.film_detail, name="film_detail"),
    path("favorites/toggle/<slug:slug>/", views.favorites_toggle, name="favorites_toggle"),
    path("favorites/", views.favorites_list, name="favorites_list"),
    path("community/", views.community, name="community"),
    path("library/", views.library, name="library"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<slug:slug>/", views.cart_add, name="cart_add"),
    path("cart/remove/<slug:slug>/", views.cart_remove, name="cart_remove"),
    path("search/", views.search, name="search"),
]
