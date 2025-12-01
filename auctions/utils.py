from .models import Listing, Watchlist

def get_current_price(listing):
    highest_bid = listing.bids.order_by("-amount").first()
    return highest_bid.amount if highest_bid else listing.starting_bid

def add_to_watchlist(user, listing):
    # Adds a listing to the user's watchlist
    Watchlist.objects.get_or_create(user=user, listing=listing)

def remove_from_watchlist(user, listing):
    # Removes a listing from the user's watchlist
    Watchlist.objects.filter(user=user, listing=listing).delete()