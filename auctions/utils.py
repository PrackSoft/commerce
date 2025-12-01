from .models import Listing

def get_current_price(listing):
    highest_bid = listing.bids.order_by("-amount").first()
    return highest_bid.amount if highest_bid else listing.starting_bid