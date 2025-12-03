from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # New paths
    path("create_listing/", views.create_listing, name="create_listing"), # Route to create a new auction listing
    path("listing/<int:listing_id>/", views.listing_detail, name="listing_detail"), # Route to view the detail page of a specific listing
    path("listing/<int:listing_id>/watchlist/", views.toggle_watchlist, name="toggle_watchlist"),
    path("listing/<int:listing_id>/bid/", views.place_bid, name="place_bid"),
    path("close/<int:listing_id>", views.close_auction, name="close_auction"),
    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("watchlist/", views.watchlist, name="watchlist"),
    # Página que lista TODAS las categorías
    path("categories/", views.categories_view, name="categories"),
    # Página que lista los listings filtrados por UNA categoría
    path("categories/<str:category_name>/", views.category_listings, name="category_listings"),  # listings por categoría
]
