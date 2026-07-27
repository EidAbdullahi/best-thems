from django.db import models

class SiteSettings(models.Model):
    """Global site configuration (singleton pattern)"""
    site_title = models.CharField(max_length=100, default="Eagle Security Service")
    tagline = models.CharField(max_length=200, default="Elite Private Protection")
    hero_title_line1 = models.CharField(max_length=100, default="Protecting What")
    hero_title_line2 = models.CharField(max_length=100, default="Matters Most")
    hero_subtitle = models.TextField(default="Eagle Security Service delivers elite private protection...")
    hero_badge_text = models.CharField(max_length=50, default="24/7 Active Protection")
    hero_eagle_image = models.ImageField(upload_to='hero/', blank=True, null=True)
    cta_primary_text = models.CharField(max_length=50, default="Request Security")
    cta_secondary_text = models.CharField(max_length=50, default="Our Services")
    contact_phone = models.CharField(max_length=30, default="+1 (234) 567-890")
    contact_email = models.EmailField(default="info@eaglesecurity.com")
    contact_address = models.TextField(default="123 Security Plaza, Suite 500\nNew York, NY 10001")
    footer_text = models.TextField(default="Elite private security services protecting what matters most.")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        # Ensures only one active settings record exists
        if self.is_active:
            SiteSettings.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class HeroStat(models.Model):
    """Animated counter stats in hero section"""
    label = models.CharField(max_length=50)
    count = models.PositiveIntegerField(default=0)
    suffix = models.CharField(max_length=10, blank=True, default="+")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label}: {self.count}{self.suffix}"


class Service(models.Model):
    """Services grid cards"""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='services/')
    icon_svg = models.TextField(help_text="Paste SVG path data here")
    link_text = models.CharField(max_length=50, default="Learn More")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class AboutSection(models.Model):
    """About section content"""
    title_line1 = models.CharField(max_length=100, default="Trusted Guardians of")
    title_line2 = models.CharField(max_length=100, default="Your Safety")
    content_paragraph1 = models.TextField()
    content_paragraph2 = models.TextField(blank=True)
    image = models.ImageField(upload_to='about/')
    experience_years = models.PositiveIntegerField(default=25)
    experience_text = models.CharField(max_length=50, default="Years of Excellence")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Section"
        verbose_name_plural = "About Section"

    def __str__(self):
        return "About Section"


class AboutFeature(models.Model):
    """Bullet features under About section"""
    about = models.ForeignKey(AboutSection, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Sector(models.Model):
    """Industries/sectors grid"""
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='sectors/')
    icon_svg = models.TextField(help_text="Paste SVG path data here")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class WhyChooseUs(models.Model):
    """Why Choose Us cards"""
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='why_us/', blank=True)
    icon_svg = models.TextField(help_text="Paste SVG path data here", blank=True)
    number = models.CharField(max_length=10, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Partner(models.Model):
    """Partners carousel"""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    image = models.ImageField(upload_to='partners/', blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


from django.core.validators import MinValueValidator, MaxValueValidator

class Testimonial(models.Model):
    quote = models.TextField()
    author_name = models.CharField(max_length=100)
    author_title = models.CharField(max_length=100)
    author_image = models.ImageField(upload_to='testimonials/', blank=True)
    background_image = models.ImageField(upload_to='testimonials/bg/', blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # ADD THIS
    rating = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])

    @property
    def empty_stars(self):
        return 5 - self.rating

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.author_name} - {self.author_title}"
    
    

    def __str__(self):
        return f"{self.author_name} - {self.author_title}"

   
class ContactMessage(models.Model):
    """Contact form submissions"""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    sector = models.CharField(max_length=50, blank=True, choices=[
        ('', 'Select Your Sector'),
        ('corporate', 'Corporate & Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('retail', 'Retail & Hospitality'),
        ('energy', 'Energy & Utilities'),
        ('government', 'Government'),
        ('transport', 'Transportation'),
        ('construction', 'Construction'),
        ('residential', 'Residential'),
        ('other', 'Other'),
    ])
    service = models.CharField(max_length=50, blank=True, choices=[
        ('', 'Select Service Type'),
        ('corporate', 'Corporate Security'),
        ('residential', 'Residential Protection'),
        ('surveillance', 'Surveillance Systems'),
        ('event', 'Event Security'),
        ('logistics', 'Logistics & Transport'),
        ('crisis', 'Crisis Response'),
        ('consultation', 'Security Consultation'),
    ])
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    

# Add this to your models.py if ContactMessage doesn't exist yet:

from django.db import models


class ContactMessage(models.Model):
    """Stores contact form submissions."""

    SECTOR_CHOICES = [
        ('corporate', 'Corporate & Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('retail', 'Retail & Hospitality'),
        ('energy', 'Energy & Utilities'),
        ('government', 'Government'),
        ('transport', 'Transportation'),
        ('construction', 'Construction'),
        ('residential', 'Residential'),
        ('other', 'Other'),
    ]

    SERVICE_CHOICES = [
        ('corporate', 'Corporate Security'),
        ('residential', 'Residential Protection'),
        ('surveillance', 'Surveillance Systems'),
        ('event', 'Event Security'),
        ('logistics', 'Logistics & Transport'),
        ('crisis', 'Crisis Response'),
        ('consultation', 'Security Consultation'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    sector = models.CharField(max_length=50, choices=SECTOR_CHOICES, blank=True)
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"