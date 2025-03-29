from django import forms
from .models import Proposal
from club.models import ClubMembership

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = [
            'title',
            'description',
            'budget',
            'timeline',
            'complexity',
            'club'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your project',
                'rows': 5
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project budget'
            }),
            'timeline': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Timeline in days'
            }),
            'complexity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'Complexity (0 to 10)'
            }),
            
            'club': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        
    #def __init__(self, *args, **kwargs):
    #    user = kwargs.pop('user', None)
    #    super().__init__(*args, **kwargs)
    #    if user:
    #        # Only allow clubs the user is a member of
    #        self.fields['club'].queryset = ClubMembership.objects.filter(user=user)
#