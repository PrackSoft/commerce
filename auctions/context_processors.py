# auctions/context_processors.py
from .models import Watchlist

def watchlist_count(request):
    # Returns the number of items in the user's watchlist for all templates
    count = 0
    if request.user.is_authenticated:
        count = Watchlist.objects.filter(user=request.user).count()
    return {"watchlist_count": count}