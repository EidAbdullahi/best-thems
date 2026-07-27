from django import forms
from django.core.validators import RegexValidator
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Contact form with honeypot anti-spam field."""

    # Honeypot field - hidden from users, bots will fill it
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}),
        initial=''
    )

    phone = forms.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[+]?[\d\s\-()]{7,20}$',
                message='Enter a valid phone number.',
                code='invalid_phone'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': '+1 (234) 567-890'
        })
    )

    class Meta:
        model = ContactMessage
        fields = ['first_name', 'last_name', 'email', 'phone', 'sector', 'service', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'John',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Doe',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'john@example.com',
                'required': True
            }),
            'sector': forms.Select(attrs={}),
            'service': forms.Select(attrs={}),
            'message': forms.Textarea(attrs={
                'placeholder': 'Describe your security needs...',
                'rows': 5
            }),
        }

    def clean_website(self):
        """Honeypot check - if filled, it's a bot."""
        website = self.cleaned_data.get('website', '')
        if website:
            raise forms.ValidationError("Bot detected!")
        return website

    def clean_message(self):
        """Basic message validation."""
        message = self.cleaned_data.get('message', '')
        if len(message) < 10:
            raise forms.ValidationError("Please provide more details (at least 10 characters).")
        return message

from django import forms
from django.core.validators import RegexValidator
from .models import (
    SiteSettings, HeroStat, Service, AboutSection, AboutFeature,
    Sector, WhyChooseUs, Partner, Testimonial, ContactMessage
)


class SiteSettingsForm(forms.ModelForm):
    """Form for editing site-wide settings."""

    class Meta:
        model = SiteSettings
        fields = [
            'site_title', 'tagline', 'hero_title_line1', 'hero_title_line2',
            'hero_subtitle', 'hero_badge_text', 'hero_eagle_image',
            'cta_primary_text', 'cta_secondary_text',
            'contact_phone', 'contact_email', 'contact_address',
            'footer_text', 'is_active'
        ]
        widgets = {
            'site_title': forms.TextInput(attrs={'class': 'admin-input'}),
            'tagline': forms.TextInput(attrs={'class': 'admin-input'}),
            'hero_title_line1': forms.TextInput(attrs={'class': 'admin-input'}),
            'hero_title_line2': forms.TextInput(attrs={'class': 'admin-input'}),
            'hero_subtitle': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 4}),
            'hero_badge_text': forms.TextInput(attrs={'class': 'admin-input'}),
            'cta_primary_text': forms.TextInput(attrs={'class': 'admin-input'}),
            'cta_secondary_text': forms.TextInput(attrs={'class': 'admin-input'}),
            'contact_phone': forms.TextInput(attrs={'class': 'admin-input'}),
            'contact_email': forms.EmailInput(attrs={'class': 'admin-input'}),
            'contact_address': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 3}),
            'footer_text': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 3}),
        }


class HeroStatForm(forms.ModelForm):
    """Form for hero statistics."""

    class Meta:
        model = HeroStat
        fields = ['label', 'count', 'suffix', 'order', 'is_active']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'admin-input', 'placeholder': 'e.g., Years Experience'}),
            'count': forms.NumberInput(attrs={'class': 'admin-input', 'placeholder': 'e.g., 25'}),
            'suffix': forms.TextInput(attrs={'class': 'admin-input', 'placeholder': 'e.g., + or %'}),
            'order': forms.NumberInput(attrs={'class': 'admin-input'}),
        }


class ServiceForm(forms.ModelForm):
    """Form for services."""

    class Meta:
        model = Service
        fields = ['title', 'slug', 'description', 'image', 'icon_svg', 'link_text', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'admin-input'}),
            'slug': forms.TextInput(attrs={'class': 'admin-input'}),
            'description': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 4}),
            'icon_svg': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 3, 'placeholder': '<path d="M12..."/>'}),
            'link_text': forms.TextInput(attrs={'class': 'admin-input'}),
            'order': forms.NumberInput(attrs={'class': 'admin-input'}),
        }


class SectorForm(forms.ModelForm):
    """Form for sectors."""

    class Meta:
        model = Sector
        fields = ['title', 'slug', 'description', 'image', 'icon_svg', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'admin-input'}),
            'slug': forms.TextInput(attrs={'class': 'admin-input'}),
            'description': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 3}),
            'icon_svg': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 3, 'placeholder': '<path d="M12..."/>'}),
            'order': forms.NumberInput(attrs={'class': 'admin-input'}),
        }


class TestimonialForm(forms.ModelForm):
    """Form for testimonials."""

    class Meta:
        model = Testimonial
        fields = ['quote', 'author_name', 'author_title', 'author_image', 'background_image', 'order', 'is_active']
        widgets = {
            'quote': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 5}),
            'author_name': forms.TextInput(attrs={'class': 'admin-input'}),
            'author_title': forms.TextInput(attrs={'class': 'admin-input'}),
            'order': forms.NumberInput(attrs={'class': 'admin-input'}),
        }


class PartnerForm(forms.ModelForm):
    """Form for partners."""

    class Meta:
        model = Partner
        fields = ['name', 'category', 'description', 'image', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'admin-input'}),
            'category': forms.TextInput(attrs={'class': 'admin-input', 'placeholder': 'e.g., Technology Partner'}),
            'description': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 2}),
            'order': forms.NumberInput(attrs={'class': 'admin-input'}),
        }


class WhyChooseUsForm(forms.ModelForm):
    """Form for Why Choose Us items."""

    class Meta:
        model = WhyChooseUs
        fields = ['title', 'description', 'image', 'icon_svg', 'number', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'admin-input'}),
            'description': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 3}),
            'icon_svg': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 3, 'placeholder': '<path d="M12..."/>'}),
            'number': forms.TextInput(attrs={'class': 'admin-input', 'placeholder': 'e.g., 01, 02'}),
            'order': forms.NumberInput(attrs={'class': 'admin-input'}),
        }


class AboutSectionForm(forms.ModelForm):
    """Form for About section."""

    class Meta:
        model = AboutSection
        fields = [
            'title_line1', 'title_line2', 'content_paragraph1',
            'content_paragraph2', 'image', 'experience_years',
            'experience_text', 'is_active'
        ]
        widgets = {
            'title_line1': forms.TextInput(attrs={'class': 'admin-input'}),
            'title_line2': forms.TextInput(attrs={'class': 'admin-input'}),
            'content_paragraph1': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 5}),
            'content_paragraph2': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 5}),
            'experience_years': forms.NumberInput(attrs={'class': 'admin-input'}),
            'experience_text': forms.TextInput(attrs={'class': 'admin-input'}),
        }


class AboutFeatureForm(forms.ModelForm):
    """Form for About features."""

    class Meta:
        model = AboutFeature
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'admin-input'}),
            'description': forms.TextInput(attrs={'class': 'admin-input'}),
            'order': forms.NumberInput(attrs={'class': 'admin-input'}),
        }