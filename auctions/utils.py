from .models import Listing, Watchlist
from decimal import Decimal

def get_current_price(listing): # get_current_price ensures accurate auction pricing by always returning the highest bid or the starting bid if no bids exist.
    highest_bid = listing.bids.order_by("-amount").first()
    return Decimal(highest_bid.amount) if highest_bid else Decimal(listing.starting_bid)

def add_to_watchlist(user, listing):
    Watchlist.objects.get_or_create(user=user, listing=listing) # Using get_or_create in add_to_watchlist prevents duplicate entries, maintaining database integrity.

def remove_from_watchlist(user, listing):
    # remove_from_watchlist efficiently deletes a specific watchlist entry without affecting other listings.
    Watchlist.objects.filter(user=user, listing=listing).delete()