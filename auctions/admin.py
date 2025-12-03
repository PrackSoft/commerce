from django.contrib import admin
from .models import Listing, Bid, Comment, Watchlist, User

# Admin for Listings
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'winner', 'is_active', 'category')
    list_filter = ('is_active', 'category', 'owner')
    search_fields = ('title', 'description', 'owner__username', 'category')
    ordering = ('title',)
    list_display_links = ('title',)

# Admin for Bids
@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('amount', 'bidder', 'listing', 'listing_active')
    list_filter = ('bidder', 'listing')
    search_fields = ('bidder__username', 'listing__title')

    def listing_active(self, obj):
        return obj.listing.is_active
    listing_active.boolean = True
    listing_active.short_description = 'Listing Active'

# Admin for Comments
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'listing', 'listing_active')
    list_filter = ('author', 'listing')
    search_fields = ('text', 'author__username', 'listing__title')

    def listing_active(self, obj):
        return obj.listing.is_active
    listing_active.boolean = True
    listing_active.short_description = 'Listing Active'

# Admin for Watchlist
@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing')
    list_filter = ('user',)
    search_fields = ('user__username', 'listing__title')

# Custom UserAdmin with inlines
class ListingInline(admin.TabularInline):
    model = Listing
    fk_name = 'owner'
    extra = 0
    fields = ('title', 'is_active', 'winner', 'category')

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    fields = ('amount', 'listing')

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('text', 'listing')

class WatchlistInline(admin.TabularInline):
    model = Watchlist
    extra = 0
    fields = ('listing',)

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    inlines = [ListingInline, BidInline, CommentInline, WatchlistInline]
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
