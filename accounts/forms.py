from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from uuid import uuid4

from .form_utils import BootstrapFormMixin
from .models import Profile

from .languages import available_languages
from .onboarding import CROP_CHOICES, GROWING_PLACES
from .locations import state_districts


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(label=_('Email'), max_length=254,
                            widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    first_name = forms.CharField(max_length=150, required=False)
    phone = forms.CharField(max_length=15, required=False)
    village = forms.CharField(max_length=100, required=False)
    state = forms.ChoiceField(label=_('State'))
    district = forms.ChoiceField(label=_('District'), help_text='Used for local weather forecasts.')
    preferred_language = forms.ChoiceField(choices=available_languages, initial='en')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.username = 'farmer_' + uuid4().hex
        locations = state_districts()
        empty = [('', _('— select —'))]
        self.fields['state'].choices = empty + [(s, s) for s in locations]
        state = self.data.get(self.add_prefix('state')) if self.is_bound else self.initial.get('state')
        self.fields['district'].choices = (empty + [(d, d) for d in locations.get(state, [])]
            if state else empty + [(s, [(d, d) for d in districts]) for s, districts in locations.items()])
        self.order_fields(['first_name', 'email', 'phone', 'village', 'state', 'district', 'preferred_language', 'password1', 'password2'])
        self.fields['password1'].help_text = _('Use at least 8 characters. Avoid personal details, common passwords, and numbers only.')
        self.fields['preferred_language'].help_text = _('Language used throughout the application and for voice greetings.')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('An account with this email already exists.'))
        return email

    def clean(self):
        cleaned = super().clean()
        state, district = cleaned.get('state'), cleaned.get('district')
        if district and district not in state_districts().get(state, []):
            self.add_error('district', _('Select a district in the selected state.'))
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            for field in ('phone', 'village', 'district', 'state', 'preferred_language'):
                setattr(profile, field, self.cleaned_data[field])
            profile.save()
        return user


class EmailLoginForm(BootstrapFormMixin, forms.Form):
    email = forms.CharField(label=_('Email'), max_length=254,
                            widget=forms.TextInput(attrs={'autocomplete': 'username', 'autofocus': True}))
    password = forms.CharField(label=_('Password'), strip=False,
                               widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))
    portal = forms.CharField(required=False, widget=forms.HiddenInput(), initial='farmer')

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        email, password = cleaned.get('email'), cleaned.get('password')
        portal = cleaned.get('portal') or (self.request.POST.get('portal', 'farmer') if self.request else 'farmer')
        if email and password:
            clean_val = email.strip()
            users = list(User.objects.filter(email__iexact=clean_val)[:2])
            if not users:
                users = list(User.objects.filter(username__iexact=clean_val)[:2])
            if len(users) == 1:
                self.user_cache = authenticate(self.request, username=users[0].username, password=password)
            else:
                User().set_password(password)  # Match password hashing work for unknown addresses.
            if self.user_cache is None:
                raise forms.ValidationError(_('Invalid email or password.'))
            if portal == 'admin' and not getattr(getattr(self.user_cache, 'profile', None), 'is_admin', False):
                self.user_cache = None
                raise forms.ValidationError('Access denied: This portal is for Krishi Mitra Administrators. Please switch to the Farmer Portal.')
        return cleaned

    def get_user(self):
        return self.user_cache


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    email = forms.EmailField(label=_('Email'), max_length=254, required=False,
                            widget=forms.EmailInput(attrs={'autocomplete': 'email'}))
    selected_crops = forms.MultipleChoiceField(label=_('Crop'), choices=CROP_CHOICES, required=False,
                                              widget=forms.CheckboxSelectMultiple)
    growing_place = forms.ChoiceField(label=_('Type'), choices=[('', _('— select —')), *GROWING_PLACES], required=False)
    first_name = forms.CharField(label='Your name', max_length=150, required=False,
                                 help_text='The assistant greets you by this name.')
    preferred_language = forms.ChoiceField(choices=available_languages,
                                           help_text='Language used throughout the application and for voice greetings.')

    class Meta:
        model = Profile
        fields = ('first_name', 'email', 'phone', 'village', 'district', 'state', 'preferred_language', 'selected_crops', 'growing_place')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = self.instance.user.first_name
        self.fields['email'].initial = self.instance.user.email
        self.fields['selected_crops'].widget.attrs['class'] = 'farm-crop-options'

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower() or self.instance.user.email
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.user_id).exists():
            raise forms.ValidationError(_('An account with this email already exists.'))
        return email

    @transaction.atomic
    def save(self, commit=True):
        profile = super().save(commit=commit)
        profile.user.first_name = self.cleaned_data['first_name'].strip()
        profile.user.email = self.cleaned_data['email']
        if commit:
            profile.user.save(update_fields=['first_name', 'email'])
        return profile
