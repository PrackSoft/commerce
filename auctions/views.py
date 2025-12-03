from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.cache import never_cache

from decimal import Decimal

from .forms import ListingForm, CommentForm
from .models import User, Listing, Watchlist, Bid, Comment

from .utils import get_current_price, add_to_watchlist, remove_from_watchlist


def index(request):
    # Fetch all active listings
    active_listings = Listing.objects.filter(is_active=True)
    for listing in active_listings:
        # Attach dynamic current price to each listing
        listing.current_price = get_current_price(listing)

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
    # Fetch listing or return 404
    listing = get_object_or_404(Listing, pk=listing_id)
    current_price = Decimal(get_current_price(listing))

    # Check if user is watching this listing
    is_watching = False
    if request.user.is_authenticated:
        is_watching = Watchlist.objects.filter(user=request.user, listing=listing).exists()

    # Determine current highest bidder
    highest_bid = listing.bids.order_by("-amount").first()
    current_owner = highest_bid.bidder.username if highest_bid else listing.owner.username

    # Prepare auction result message if closed
    show_message = False
    message = ""
    if not listing.is_active and request.user.is_authenticated:
        if request.user == listing.owner or request.user == listing.winner:
            show_message = True
            if listing.winner:
                message = f"Auction closed. Final price: ${current_price} won by {listing.winner.username}."
            else:
                message = f"Auction closed. No bids were placed. Starting bid: ${listing.starting_bid}"

    # Fetch comments for the listing
    comments = Comment.objects.filter(listing=listing).order_by('-id')
    form = CommentForm()
    error = request.GET.get("error", "")

    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "current_price": current_price,
        "is_watching": is_watching,
        "current_owner": current_owner,
        "show_message": show_message,
        "message": message,
        "comments": comments,
        "form": form,
        "error": error,
    })


@never_cache
@login_required
def toggle_watchlist(request, listing_id):
    # Add or remove listing from user's watchlist
    listing = get_object_or_404(Listing, pk=listing_id)
    if Watchlist.objects.filter(user=request.user, listing=listing).exists():
        remove_from_watchlist(request.user, listing)
    else:
        add_to_watchlist(request.user, listing)

    # Rebuild context like listing_detail
    current_price = Decimal(get_current_price(listing))
    is_watching = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    highest_bid = listing.bids.order_by("-amount").first()
    current_owner = highest_bid.bidder.username if highest_bid else listing.owner.username

    show_message = False
    message = ""
    if not listing.is_active:
        if request.user == listing.owner or request.user == listing.winner:
            show_message = True
            if listing.winner:
                message = f"Auction closed. Final price: ${current_price} won by {listing.winner.username}."
            else:
                message = f"Auction closed. No bids were placed. Starting bid: ${listing.starting_bid}"

    comments = Comment.objects.filter(listing=listing).order_by('-id')
    form = CommentForm()

    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "current_price": current_price,
        "is_watching": is_watching,
        "current_owner": current_owner,
        "show_message": show_message,
        "message": message,
        "comments": comments,
        "form": form,
        "error": "",
    })


@never_cache
@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    current_price = Decimal(get_current_price(listing))
    error = ""

    if request.method == "POST":
        try:
            bid_amount = Decimal(request.POST["bid_amount"])
        except (KeyError, ValueError):
            error = "Invalid bid amount."
        else:
            if bid_amount <= current_price:
                error = f"Your bid must be greater than the current price (${current_price})."
            else:
                # Valid bid: create bid record
                Bid.objects.create(amount=bid_amount, bidder=request.user, listing=listing)
                return redirect("listing_detail", listing_id=listing.id)

    # Rebuild context like listing_detail
    is_watching = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    highest_bid = listing.bids.order_by("-amount").first()
    current_owner = highest_bid.bidder.username if highest_bid else listing.owner.username

    show_message = False
    message = ""
    if not listing.is_active:
        if request.user == listing.owner or request.user == listing.winner:
            show_message = True
            if listing.winner:
                message = f"Auction closed. Final price: ${current_price} won by {listing.winner.username}."
            else:
                message = f"Auction closed. No bids were placed. Starting bid: ${listing.starting_bid}"

    comments = Comment.objects.filter(listing=listing).order_by('-id')
    form = CommentForm()

    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "current_price": current_price,
        "is_watching": is_watching,
        "current_owner": current_owner,
        "show_message": show_message,
        "message": message,
        "comments": comments,
        "form": form,
        "error": error,
    })


@never_cache
@login_required
def close_auction(request, listing_id):
    # Close auction and assign winner if any
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST" and request.user == listing.owner and listing.is_active:
        listing.is_active = False
        highest_bid = listing.bids.order_by("-amount").first()
        listing.winner = highest_bid.bidder if highest_bid else None
        listing.save()

    # Rebuild context like listing_detail
    current_price = Decimal(get_current_price(listing))
    is_watching = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    highest_bid = listing.bids.order_by("-amount").first()
    current_owner = highest_bid.bidder.username if highest_bid else listing.owner.username

    show_message = False
    message = ""
    if not listing.is_active:
        if request.user == listing.owner or request.user == listing.winner:
            show_message = True
            if listing.winner:
                message = f"Auction closed. Final price: ${current_price} won by {listing.winner.username}."
            else:
                message = f"Auction closed. No bids were placed. Starting bid: ${listing.starting_bid}"

    comments = Comment.objects.filter(listing=listing).order_by('-id')
    form = CommentForm()

    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "current_price": current_price,
        "is_watching": is_watching,
        "current_owner": current_owner,
        "show_message": show_message,
        "message": message,
        "comments": comments,
        "form": form,
        "error": "",
    })


@never_cache
@login_required
def add_comment(request, listing_id):
    # Add a comment to a listing
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.listing = listing
            comment.save()

    # Rebuild context like listing_detail
    current_price = Decimal(get_current_price(listing))
    is_watching = Watchlist.objects.filter(user=request.user, listing=listing).exists()
    highest_bid = listing.bids.order_by("-amount").first()
    current_owner = highest_bid.bidder.username if highest_bid else listing.owner.username

    show_message = False
    message = ""
    if not listing.is_active:
        if request.user == listing.owner or request.user == listing.winner:
            show_message = True
            if listing.winner:
                message = f"Auction closed. Final price: ${current_price} won by {listing.winner.username}."
            else:
                message = f"Auction closed. No bids were placed. Starting bid: ${listing.starting_bid}"

    comments = Comment.objects.filter(listing=listing).order_by('-id')
    form = CommentForm()

    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "current_price": current_price,
        "is_watching": is_watching,
        "current_owner": current_owner,
        "show_message": show_message,
        "message": message,
        "comments": comments,
        "form": form,
    })


@login_required
def watchlist(request):
    # Fetch all active listings in user's watchlist
    listings = Listing.objects.filter(watchlist_entries__user=request.user, is_active=True)

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
