from django import forms
from .models import Gig

class GigForm(forms.ModelForm):
    class Meta:
        model = Gig
        fields = ['category', 'title', 'description', 'price', 'delivery_time', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
