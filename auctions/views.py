from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import never_cache

from decimal import Decimal

from .forms import ListingForm, CommentForm
from .models import User, Listing, Watchlist, Bid, Comment, RemovedPurchase

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
            current_amount, has_bids = current_price(listing)

            if has_bids:
                if bid_amount <= current_amount:
                    error = f"Your bid must be greater than the current price (${current_amount})."
                else:
                    Bid.objects.create(amount=bid_amount, bidder=request.user, listing=listing)
                    return redirect("listing_detail", listing_id=listing.id)
            else:
                if bid_amount < current_amount:
                    error = f"Your bid must be at least the starting price (${current_amount})."
                else:
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
def categories_view(request):
    # Fetch all unique categories with active listings
    listings = Listing.objects.filter(is_active=True)
    categories = sorted({listing.category for listing in listings if listing.category})

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

@login_required
def unified_listings(request, mode, category_name=None):
    listings = []

    if mode == "watchlist":
        listings = Listing.objects.filter(
            watchlist_entries__user=request.user
        ).order_by('-id')

    elif mode == "my_listings":
        listings = Listing.objects.filter(owner=request.user).order_by('-id')

    elif mode == "my_purchases":
        bids = Bid.objects.filter(bidder=request.user).select_related('listing')
        listings_set = {bid.listing for bid in bids}

        removed = RemovedPurchase.objects.filter(user=request.user).values_list('listing_id', flat=True)

        listings = []
        for listing in listings_set:
            if listing.id in removed:
                continue
            if listing.owner == request.user:
                continue
            listings.append(listing)

    elif mode == "category":
        listings = Listing.objects.filter(is_active=True, category=category_name)

    current_price(listings)

    for listing in listings:
        if mode in ["my_purchases", "watchlist"]:
            if listing.is_active:
                listing.status_message = f"Current price: ${listing.current_price}"
            else:
                if listing.winner == request.user:
                    listing.status_message = "YOU WON!"
                else:
                    listing.status_message = "YOU DID NOT WIN"
        elif mode == "my_listings":
            listing.status_message = "Active" if listing.is_active else "Closed"
        else:
            listing.status_message = ""

    return render(request, "auctions/listings.html", {
        "listings": listings,
        "mode": mode,
        "category_name": category_name,
    })


@login_required
def remove_listing_from_mode(request, listing_id):
    mode = request.POST.get("mode")
    listing = Listing.objects.get(pk=listing_id)

    if mode == "watchlist":
        Watchlist.objects.filter(user=request.user, listing=listing).delete()

    elif mode == "my_purchases":
        RemovedPurchase.objects.get_or_create(user=request.user, listing=listing)

    if mode == "watchlist":
        return redirect("watchlist")
    elif mode == "my_listings":
        return redirect("my_listings")
    elif mode == "my_purchases":
        return redirect("my_purchases")
