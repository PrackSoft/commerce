from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


# My models
class Listing(models.Model):
    # Basic listing info
    title = models.CharField(max_length=100)  # Title of the listing
    description = models.TextField()          # Full description
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)  # Minimum bid
    
    # Optional fields
    image_url = models.URLField(blank=True, null=True)   # Optional image
    category = models.CharField(max_length=50, blank=True, null=True)  # Optional category
    
    # State
    is_active = models.BooleanField(default=True)  # Controls open/closed auction
    
    # Relations
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")  # Creator

    def __str__(self):
        return self.title


class Bid(models.Model):
    # Bid amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Bid value

    # Relations
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")     # Who bids
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids") # For which listing

    def __str__(self):
        return f"{self.amount}"


class Comment(models.Model):
    # Comment text
    text = models.TextField()  # Comment content
    
    # Relations
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")   # Who comments
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments") # On which listing

    def __str__(self):
        return self.text[:50]