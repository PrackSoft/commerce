from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import never_cache

from decimal import Decimal

from .forms import ListingForm, CommentForm
from .models import User, Listing, Watchlist, Bid, Comment

from .utils import current_price, add_to_watchlist, remove_from_watchlist, get_listing_context


def index(request):
    # Fetch all active listings
    active_listings = Listing.objects.filter(is_active=True)
    
    # Attach dynamic current price to each listing
    current_price(active_listings)

    return render(request, "auctions/index.html", {
        "listings": active_listings,
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    # Log out the current user
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            # Create new user
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })

        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@never_cache
@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            # Assign ownership and mark listing active
            listing.owner = request.user
            listing.is_active = True
            listing.save()
            return redirect('index')
    else:
        form = ListingForm()

    return render(request, "auctions/create_listing.html", {"form": form})

@never_cache
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    # Get context including current price and has_bids
    context = get_listing_context(listing, user=request.user, error=request.GET.get("error", ""))
    return render(request, "auctions/listing_detail.html", context)


@never_cache
@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    # Toggle watchlist
    if Watchlist.objects.filter(user=request.user, listing=listing).exists():
        remove_from_watchlist(request.user, listing)
    else:
        add_to_watchlist(request.user, listing)

    # Build context using utils
    context = get_listing_context(listing, user=request.user, error="")

    return render(request, "auctions/listing_detail.html", context)


@never_cache
@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    error = ""

    if request.method == "POST":
        try:
            bid_amount = Decimal(request.POST["bid_amount"])
        except (KeyError, ValueError):
            error = "Invalid bid amount."
        else:
            if bid_amount <= current_price(listing):
                error = f"Your bid must be greater than the current price (${current_price(listing)})."
            else:
                # Valid bid: create bid record
                Bid.objects.create(amount=bid_amount, bidder=request.user, listing=listing)
                return redirect("listing_detail", listing_id=listing.id)

    # Build context using utils
    context = get_listing_context(listing, user=request.user, error=error)

    return render(request, "auctions/listing_detail.html", context)


@never_cache
@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == "POST" and request.user == listing.owner and listing.is_active:
        highest_bid = listing.bids.order_by("-amount").first()
        listing.is_active = False
        listing.winner = highest_bid.bidder if highest_bid else None
        listing.save()

    # Build context using utils
    context = get_listing_context(listing, user=request.user)

    return render(request, "auctions/listing_detail.html", context)


@never_cache
@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.listing = listing
            comment.save()

    # Build context using utils
    context = get_listing_context(listing, user=request.user)
    return render(request, "auctions/listing_detail.html", context)


@login_required
def watchlist(request):
    # Fetch all active listings in user's watchlist
    listings = Listing.objects.filter(watchlist_entries__user=request.user, is_active=True)
    
    # Attach dynamic current price to each listing
    current_price(listings)

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


@login_required
def category_listings(request, category_name):
    # Fetch all active listings in a specific category
    listings = Listing.objects.filter(is_active=True, category=category_name)
    return render(request, "auctions/category_listings.html", {
        "category_name": category_name,
        "listings": listings
    })


@login_required
def categories_view(request):
    # Fetch all unique categories with active listings
    listings = Listing.objects.filter(is_active=True)
    categories = sorted({listing.category for listing in listings if listing.category})

    return render(request, "auctions/categories.html", {
        "categories": categories
    })


@login_required
def my_purchases(request):
    # Fetch all listings where user placed a bid
    bids = Bid.objects.filter(bidder=request.user).select_related('listing')
    listings = {bid.listing for bid in bids}  # Remove duplicates

    # Filter listings
    visible_listings = []
    for listing in listings:
        if listing.owner == request.user:
            continue  # Owner never sees their own listings
        if listing.is_active:
            visible_listings.append(listing)
        else:
            # Show inactive only if user is winner
            if listing.winner == request.user:
                visible_listings.append(listing)

    # Attach current price to each listing
    current_price(visible_listings)

    return render(request, "auctions/my_purchases.html", {
        "listings": visible_listings
    })


@login_required
def my_listings(request):
    # Fetch all listings created by the current user (both active and inactive)
    listings = Listing.objects.filter(owner=request.user).order_by('-id')
    
    # Attach current price to each listing
    current_price(listings)

    return render(request, "auctions/my_listings.html", {
        "listings": listings
    })