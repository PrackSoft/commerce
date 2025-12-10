from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


CATEGORY_CHOICES = [
    ("Fashion", "Fashion"),
    ("Toys", "Toys"),
    ("Electronics", "Electronics"),
    ("Home", "Home"),
    ("Books", "Books"),
]


class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="won_listings")
    is_active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(starting_bid__gt=0), name="starting_bid_gt_0")
        ]

    def __str__(self):
        return self.title


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_entries")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist_entries")

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"


class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.amount}"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return self.text[:50]


class RemovedPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'listing')
