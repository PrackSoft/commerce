from django import forms
from .models import Listing, Comment

class ListingForm(forms.ModelForm):
class Meta:
model = Listing
fields = ['title', 'description', 'starting_bid', 'category', 'image_url']

class CommentForm(forms.ModelForm):
class Meta:
model = Comment
fields = ['text']