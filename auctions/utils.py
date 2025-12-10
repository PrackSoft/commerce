from .models import Listing, Watchlist, Comment
from decimal import Decimal
from collections.abc import Iterable
from .forms import CommentForm

def is_watching(user, listing):
    """Return True if user has listing in watchlist."""
    return Watchlist.objects.filter(user=user, listing=listing).exists()


def current_price(listings):
    """
    If `listings` is a single Listing, returns its current price.
    If `listings` is an iterable of Listings, attaches `current_price` to each and returns the iterable.
    """
    # Single Listing
    if isinstance(listings, Listing):
        has_bids = listings.bids.exists()
        highest_bid = listings.bids.order_by("-amount").first()
        price = Decimal(highest_bid.amount) if highest_bid else Decimal(listings.starting_bid)
        return price, has_bids

    # Iterable of Listings
    if isinstance(listings, Iterable):
        listings = list(listings)  # Ensure it's iterable
        for listing in listings:
            if not isinstance(listing, Listing):
                continue
            has_bids = listing.bids.exists()
            highest_bid = listing.bids.order_by("-amount").first()
            listing.current_price = Decimal(highest_bid.amount) if highest_bid else Decimal(listing.starting_bid)
            listing.has_bids = has_bids
        return listings

    raise TypeError("Argument must be a Listing or an iterable of Listings.")


def get_listing_context(listing, user=None, error=""):
    """
    Build context dictionary for a listing page.
    Includes current price, watching status, owner, messages, comments, and comment form.
    """
    if isinstance(listing, Listing):
        current_price_value, has_bids = current_price(listing)
    else:
        current_price_value, has_bids = 0, False

    is_watching_value = is_watching(user, listing) if user and hasattr(user, 'is_authenticated') and user.is_authenticated else False

    highest_bid = listing.bids.order_by("-amount").first()
    current_owner = highest_bid.bidder.username if highest_bid else listing.owner.username

    show_message = False
    message = ""
    if not listing.is_active and user is not None and hasattr(user, 'is_authenticated') and user.is_authenticated:
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
        "has_bids": has_bids,
        "current_price": current_price_value,
        "is_watching": is_watching_value,
        "current_owner": current_owner,
        "show_message": show_message,
        "message": message,
        "comments": comments,
        "form": form,
        "error": error,
    }


def add_to_watchlist(user, listing):
    Watchlist.objects.get_or_create(user=user, listing=listing)

def remove_from_watchlist(user, listing):
    Watchlist.objects.filter(user=user, listing=listing).delete()
