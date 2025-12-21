from django.contrib import admin
from .models import Listing, Bid, Comment, Watchlist, User

# ListingAdmin
# Configures how listings appear in the admin, including which fields to display, filter, search, and link.
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'winner', 'is_active', 'category')
    list_filter = ('is_active', 'category', 'owner')
    search_fields = ('title', 'description', 'owner__username', 'category')
    ordering = ('title',)
    list_display_links = ('title',)

# BidAdmin
# Shows bids with a custom boolean field listing_active to indicate if the associated listing is active, improving admin clarity.
@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('amount', 'bidder', 'listing', 'listing_active')
    list_filter = ('bidder', 'listing')
    search_fields = ('bidder__username', 'listing__title')

    def listing_active(self, obj):
        return obj.listing.is_active
    listing_active.boolean = True
    listing_active.short_description = 'Listing Active'

# CommentAdmin
# Displays comments with the listing_active boolean for quick status checks of the related listing.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'listing', 'listing_active')
    list_filter = ('author', 'listing')
    search_fields = ('text', 'author__username', 'listing__title')

    def listing_active(self, obj):
        return obj.listing.is_active
    listing_active.boolean = True
    listing_active.short_description = 'Listing Active'

# WatchlistAdmin
# Manages user watchlists with filters and search for efficient lookup.
@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing')
    list_filter = ('user',)
    search_fields = ('user__username', 'listing__title')

# ListingInline
# Allows inline editing of listings directly from the user admin page, improving workflow.
class ListingInline(admin.TabularInline):
    model = Listing
    fk_name = 'owner'
    extra = 0
    fields = ('title', 'is_active', 'winner', 'category')

# BidInline
# Allows inline editing of bids in the user admin for quick access.
class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    fields = ('amount', 'listing')

# CommentInline
# Enables inline editing of comments from the user admin page.
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('text', 'listing')

# WatchlistInline
# Shows a user’s watchlist inline within the user admin for easy management.
class WatchlistInline(admin.TabularInline):
    model = Watchlist
    extra = 0
    fields = ('listing',)

# CustomUserAdmin
# Extends the user admin to include all related inlines and searchable fields, giving a comprehensive overview of user activity.
@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    inlines = [ListingInline, BidInline, CommentInline, WatchlistInline]
    list_display = ('username', 'email', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

# Additional notes:
# Custom boolean fields like listing_active improve clarity in the admin interface.
# Using extra=0 in inlines prevents unnecessary empty rows, keeping the admin clean.
# Proper use of list_filter, search_fields, and list_display enhances admin usability and efficiency.