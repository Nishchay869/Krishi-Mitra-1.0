from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .form_utils import BootstrapFormMixin
from .models import Profile

LANGUAGE_CHOICES = [('en', 'English'), ('hi', 'Hindi'), ('kn', 'Kannada'), ('te', 'Telugu'),
                    ('ta', 'Tamil'), ('mr', 'Marathi')]


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150, required=False)
    phone = forms.CharField(max_length=15, required=False)
    village = forms.CharField(max_length=100, required=False)
    district = forms.CharField(max_length=100, required=False, help_text='Used for local weather forecasts.')
    state = forms.CharField(max_length=100, required=False)
    preferred_language = forms.ChoiceField(choices=LANGUAGE_CHOICES, initial='en')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name')

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            for field in ('phone', 'village', 'district', 'state', 'preferred_language'):
                setattr(profile, field, self.cleaned_data[field])
            profile.save()
        return user


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    preferred_language = forms.ChoiceField(choices=LANGUAGE_CHOICES)

    class Meta:
        model = Profile
        fields = ('phone', 'village', 'district', 'state', 'preferred_language')
