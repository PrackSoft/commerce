from .models import Listing, Watchlist
from decimal import Decimal
from collections.abc import Iterable


# current_price ensures accurate auction pricing by always returning the highest bid or the starting bid if no bids exist.
def current_price(listings):
    """
    If `listings` is a single listing, returns its current price.
    If `listings` is an iterable of listings, attaches `current_price` to each and returns the iterable.
    """
    # Detect single listing
    if hasattr(listings, "bids"):
        highest_bid = listings.bids.order_by("-amount").first()
        return Decimal(highest_bid.amount) if highest_bid else Decimal(listings.starting_bid)
    
    # Detect iterable of listings
    if isinstance(listings, Iterable):
        for listing in listings:
            highest_bid = listing.bids.order_by("-amount").first()
            listing.current_price = Decimal(highest_bid.amount) if highest_bid else Decimal(listing.starting_bid)
        return listings

    # Neither single listing nor iterable
    raise TypeError("Argument must be a Listing or an iterable of Listings.")


def add_to_watchlist(user, listing):
    Watchlist.objects.get_or_create(user=user, listing=listing) # Using get_or_create in add_to_watchlist prevents duplicate entries, maintaining database integrity.

def remove_from_watchlist(user, listing):
    # remove_from_watchlist efficiently deletes a specific watchlist entry without affecting other listings.
    Watchlist.objects.filter(user=user, listing=listing).delete()