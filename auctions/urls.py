from django.urls import path
from . import views

urlpatterns = [
    # Home page showing all active listings
    path("", views.index, name="index"),

    # Authentication routes
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),

    # Create listing
    path("create/", views.create_listing, name="create_listing"),

    # Listing page
    path("listing/<int:listing_id>/", views.listing_detail, name="listing_detail"),
    path("listing/<int:listing_id>/bid/", views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/close/", views.close_auction, name="close_auction"),
    path("listing/<int:listing_id>/comment/", views.add_comment, name="add_comment"),
    path("listing/<int:listing_id>/watchlist/", views.toggle_watchlist, name="toggle_watchlist"),
    path("listing/<int:listing_id>/remove/", views.remove_listing_from_mode, name="remove_listing_from_mode"),

    # Unified listings views: watchlist, category listings, my listings, and my purchases
    path("watchlist/", views.unified_listings, {"mode": "watchlist"}, name="watchlist"),
    path("category/<str:category_name>/", views.unified_listings, {"mode": "category"}, name="category_listings"),
    path("my_listings/", views.unified_listings, {"mode": "my_listings"}, name="my_listings"),
    path("my_purchases/", views.unified_listings, {"mode": "my_purchases"}, name="my_purchases"),

    # Categories
    path("categories/", views.categories_view, name="categories"),
]
