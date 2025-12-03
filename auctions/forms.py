from django import forms
from .models import Listing, Comment

# Defines a ModelForm for Listing to automatically generate input fields based on the model, reducing repetitive code.
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        # CommentForm uses a Textarea widget to improve UX for multi-line text input.
        widgets = {
            'text': forms.Textarea(attrs={
                # Limiting rows and cols provides consistent form layout and prevents overly large input areas.
                'rows': 2, 
                'cols': 40,
                # Adding placeholder in the widget guides users on what to enter, enhancing usability.
                'placeholder': 'Write a comment...'
                }) 
            }