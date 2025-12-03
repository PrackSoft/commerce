from django.urls import path
from . import views

urlpatterns = [
    # Home page showing all active listings
    path("", views.index, name="index"),

    # Authentication routes
    path("login", views.login_view, name="login"),   # User login
    path("logout", views.logout_view, name="logout"), # User logout
    path("register", views.register, name="register"), # User registration

    # Auction listing creation
    path("create_listing/", views.create_listing, name="create_listing"), 
    # Route to create a new auction listing. Only accessible by logged-in users.

    # Individual listing detail page
    path("listing/<int:listing_id>/", views.listing_detail, name="listing_detail"), 
    # Shows all information about a specific listing, including bids, comments, and watchlist controls.

    # Watchlist toggle
    path("listing/<int:listing_id>/watchlist/", views.toggle_watchlist, name="toggle_watchlist"), 
    # Adds/removes the listing to/from the current user's watchlist.

    # Placing a bid
    path("listing/<int:listing_id>/bid/", views.place_bid, name="place_bid"), 
    # Handles submitting a new bid for a listing.

    # Closing an auction
    path("close/<int:listing_id>", views.close_auction, name="close_auction"), 
    # Allows the owner to close the auction and determine the winner.

    # Adding a comment
    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment"), 
    # Handles submitting comments for a listing.

    # User's watchlist
    path("watchlist/", views.watchlist, name="watchlist"), 
    # Displays all listings the current user has added to their watchlist.

    # Categories pages
    path("categories/", views.categories_view, name="categories"), 
    # Page showing all categories of active listings.

    path("categories/<str:category_name>/", views.category_listings, name="category_listings"), 
    # Page showing all active listings filtered by the selected category.
]
