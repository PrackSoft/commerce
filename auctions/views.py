from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import ListingForm
from .models import User, Listing, Watchlist

from .utils import get_current_price, add_to_watchlist, remove_from_watchlist



#def index(request):
    #active_listings = Listing.objects.filter(is_active=True) # fetch all active listings from the database...
    #return render(request, "auctions/index.html", {"listings": active_listings}) # ...and pass them to the template
def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    for listing in active_listings:
        listing.current_price = get_current_price(listing)  # attach current price to each listing
    return render(request, "auctions/index.html", {"listings": active_listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
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
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
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

# My views
@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user  # assign the owner of the listing
            listing.active = True         # mark the listing as active
            listing.save()
            return redirect('index')
    else:
        form = ListingForm()
    return render(request, "auctions/create_listing.html", {"form": form})

def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    current_price = get_current_price(listing)

    is_watching = False
    if request.user.is_authenticated:
        is_watching = Watchlist.objects.filter(user=request.user, listing=listing).exists()

    return render(request, "auctions/listing_detail.html", {
    "listing": listing,
    "current_price": current_price,
    "is_watching": is_watching
})

@login_required
def toggle_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if Watchlist.objects.filter(user=request.user, listing=listing).exists():
        remove_from_watchlist(request.user, listing)
    else:
        add_to_watchlist(request.user, listing)
    return redirect('listing_detail', listing_id=listing.id)

