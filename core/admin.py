from django.contrib import admin
from .models import (
    SiteSettings, HeroStat, Service, AboutSection,
    AboutFeature, Sector, WhyChooseUs, Partner,
    Testimonial, ContactMessage
)

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_title', 'is_active']

@admin.register(HeroStat)
class HeroStatAdmin(admin.ModelAdmin):
    list_display = ['label', 'count', 'order', 'is_active']
    list_editable = ['order', 'is_active']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    list_display = ['title_line1', 'title_line2', 'is_active']

class AboutFeatureInline(admin.TabularInline):
    model = AboutFeature
    extra = 1

@admin.register(AboutFeature)
class AboutFeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'about', 'order']

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(WhyChooseUs)
class WhyChooseUsAdmin(admin.ModelAdmin):
    list_display = ['title', 'number', 'order', 'is_active']
    list_editable = ['order', 'is_active']

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'order', 'is_active']
    list_editable = ['order', 'is_active']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_title', 'order', 'is_active']
    list_editable = ['order', 'is_active']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'sector', 'service', 'created_at', 'is_read']
    list_filter = ['sector', 'service', 'is_read', 'created_at']
    list_editable = ['is_read']
    readonly_fields = ['created_at']