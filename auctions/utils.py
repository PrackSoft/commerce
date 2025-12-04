from .models import Listing, Watchlist, Comment
from decimal import Decimal
from collections.abc import Iterable
from .forms import CommentForm


def is_watching(user, listing):
    """Return True if user has listing in watchlist."""
    return Watchlist.objects.filter(user=user, listing=listing).exists()


def get_listing_context(listing, user=None, error=""):
    """
    Build context dictionary for a listing page.
    """
    current_price_value, has_bids = current_price(listing)  # unpack tuple
    is_watching_value = is_watching(user, listing) if user else False

    highest_bid = listing.bids.order_by("-amount").first()
    current_owner = highest_bid.bidder.username if highest_bid else listing.owner.username

    show_message = False
    message = ""
    if not listing.is_active and user is not None:
        if user == listing.owner or user == listing.winner:
            show_message = True
            if listing.winner:
                message = f"Auction closed. Final price: ${current_price_value} won by {listing.winner.username}."
            else:
                message = f"Auction closed. No bids were placed. Starting bid: ${listing.starting_bid}"

    comments = Comment.objects.filter(listing=listing).order_by('-id')
    form = CommentForm()

    return {
        "listing": listing,
        "starting_bid": listing.starting_bid,
        "current_price": current_price_value,  # solo el número
        "has_bids": has_bids,
        "is_watching": is_watching_value,
        "current_owner": current_owner,
        "show_message": show_message,
        "message": message,
        "comments": comments,
        "form": form,
        "error": error,
    }



def current_price(listings):
    """
    If `listings` is a single listing, returns its current price.
    If `listings` is an iterable of listings, attaches `current_price` to each and returns the iterable.
    """
    # Single listing
    if hasattr(listings, "bids"):
        has_bids = listings.bids.exists()
        highest_bid = listings.bids.order_by("-amount").first()
        price = Decimal(highest_bid.amount) if highest_bid else Decimal(listings.starting_bid)
        return price, has_bids

    # Iterable of listings
    if isinstance(listings, Iterable):
        for listing in listings:
            has_bids = listing.bids.exists()
            highest_bid = listing.bids.order_by("-amount").first()
            listing.current_price = Decimal(highest_bid.amount) if highest_bid else Decimal(listing.starting_bid)
            listing.has_bids = has_bids
        return listings

    raise TypeError("Argument must be a Listing or an iterable of Listings.")



def add_to_watchlist(user, listing):
    Watchlist.objects.get_or_create(user=user, listing=listing) # Using get_or_create in add_to_watchlist prevents duplicate entries, maintaining database integrity.

def remove_from_watchlist(user, listing):
    # remove_from_watchlist efficiently deletes a specific watchlist entry without affecting other listings.
    Watchlist.objects.filter(user=user, listing=listing).delete()