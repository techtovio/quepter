from django import forms
from .models import Talent, Booking, Review

class TalentForm(forms.ModelForm):
    class Meta:
        model = Talent
        fields = ['name', 'bio', 'category', 'price_per_hour', 'profile_image', 'video_demo']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'price_per_hour': 'Price per hour ($)'
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'duration_hours']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'duration_hours': forms.NumberInput(attrs={'min': 1, 'max': 8, 'step': 0.5})
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3})
        }