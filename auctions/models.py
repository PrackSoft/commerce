from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Custom user model extending Django's AbstractUser, allowing future customization if needed.
    pass


# My models
CATEGORY_CHOICES = [
    ("Toys", "Toys"),
    ("Books", "Books"),
    ("Clothing", "Clothing"),
    ("Electronics", "Electronics"),
]

class Listing(models.Model):
    # Represents an auction listing with title, description, starting bid, optional image, category, and owner.
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(
        max_digits=10, 
        decimal_places=2
        )
    
    # Optional fields.
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=True,
        null=True
        )
    winner = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name="won_listings"
        )

    # State.
    is_active = models.BooleanField(default=True)
    
    # Relations.
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="listings"
        )

    class Meta:
            constraints = [
                models.CheckConstraint(
                    check=models.Q(starting_bid__gt=0), 
                    name="starting_bid_gt_0"
                    )
                ]

    def __str__(self):
        return self.title
    # Interesting points:
    #   Enforces positive starting bids with a database-level constraint.
    #   `is_active` tracks open/closed auction state for business logic.
    #   Optional fields allow flexibility while maintaining structured data.


class Watchlist(models.Model):
    # Represents a user's watchlist entries linking users to listings they follow.
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="watchlist_entries"
        )
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name="watchlist_entries"
        )

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"
    # Interesting points:
    #   Enables reverse lookups from both User and Listing.
    #   Supports watchlist functionality without storing extra redundant data.


class Bid(models.Model):
    # Represents a bid placed by a user on a listing.
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2
        )

    bidder = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="bids"
        )
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name="bids"
        )

    def __str__(self):
        return f"{self.amount}"
    # Interesting points:
    #   Tracks bid amount and ownership clearly.
    #   Allows efficient aggregation and retrieval of highest bid per listing.


class Comment(models.Model):
    # Represents a comment made by a user on a listing.
    text = models.TextField()
    
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="comments"
        )
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name="comments"
        )

    def __str__(self):
        return self.text[:50]
    # Interesting points:
    #   Stores relational information for easy comment display per listing.
    #   `__str__` method truncates for readability in admin and logs.