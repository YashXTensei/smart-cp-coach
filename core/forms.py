from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProblem, Problem

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# 🧠 MANUAL PROBLEM FORM
class ManualProblemForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label="Problem Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Two Sum'
        })
    )

    rating = forms.IntegerField(
        required=False,
        label="Rating (optional)",
        min_value=800,
        max_value=3500,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. 1400'
        })
    )

    difficulty = forms.ChoiceField(
        choices=Problem.DIFFICULTY_CHOICES,
        label="Difficulty",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    status = forms.ChoiceField(
        choices=UserProblem.STATUS_CHOICES,
        label="Status",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    tags = forms.CharField(
        required=False,
        label="Tags (optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. dp, greedy, graphs'
        })
    )

    notes = forms.CharField(
        required=False,
        label="Notes",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Approach, key observations...'
        })
    )


# 📌 USER PROBLEM FORM
class UserProblemForm(forms.ModelForm):
    class Meta:
        model = UserProblem
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your approach, mistakes, learnings...'
            }),
        }