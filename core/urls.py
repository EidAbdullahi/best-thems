from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),

    # Admin Authentication
    path('admin/login/', views.admin_login, name='admin_login'),

    # Admin Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Site Settings
    path('admin/settings/', views.admin_settings, name='admin_settings'),

    # Hero Stats
    path('admin/hero-stats/', views.admin_hero_stats, name='admin_hero_stats'),
    path('admin/hero-stats/add/', views.admin_hero_stat_add, name='admin_hero_stat_add'),
    path('admin/hero-stats/<int:pk>/edit/', views.admin_hero_stat_edit, name='admin_hero_stat_edit'),
    path('admin/hero-stats/<int:pk>/delete/', views.admin_hero_stat_delete, name='admin_hero_stat_delete'),

    # Services
    path('admin/services/', views.admin_services, name='admin_services'),
    path('admin/services/add/', views.admin_service_add, name='admin_service_add'),
    path('admin/services/<int:pk>/edit/', views.admin_service_edit, name='admin_service_edit'),
    path('admin/services/<int:pk>/delete/', views.admin_service_delete, name='admin_service_delete'),
    path('admin/services/<int:pk>/toggle/', views.admin_service_toggle, name='admin_service_toggle'),

    # Sectors
    path('admin/sectors/', views.admin_sectors, name='admin_sectors'),
    path('admin/sectors/add/', views.admin_sector_add, name='admin_sector_add'),
    path('admin/sectors/<int:pk>/edit/', views.admin_sector_edit, name='admin_sector_edit'),
    path('admin/sectors/<int:pk>/delete/', views.admin_sector_delete, name='admin_sector_delete'),
    path('admin/sectors/<int:pk>/toggle/', views.admin_sector_toggle, name='admin_sector_toggle'),

    # Testimonials
    path('admin/testimonials/', views.admin_testimonials, name='admin_testimonials'),
    path('admin/testimonials/add/', views.admin_testimonial_add, name='admin_testimonial_add'),
    path('admin/testimonials/<int:pk>/edit/', views.admin_testimonial_edit, name='admin_testimonial_edit'),
    path('admin/testimonials/<int:pk>/delete/', views.admin_testimonial_delete, name='admin_testimonial_delete'),
    path('admin/testimonials/<int:pk>/toggle/', views.admin_testimonial_toggle, name='admin_testimonial_toggle'),

    # Partners
    path('admin/partners/', views.admin_partners, name='admin_partners'),
    path('admin/partners/add/', views.admin_partner_add, name='admin_partner_add'),
    path('admin/partners/<int:pk>/edit/', views.admin_partner_edit, name='admin_partner_edit'),
    path('admin/partners/<int:pk>/delete/', views.admin_partner_delete, name='admin_partner_delete'),
    path('admin/partners/<int:pk>/toggle/', views.admin_partner_toggle, name='admin_partner_toggle'),

    # Why Choose Us
    path('admin/why-us/', views.admin_why_us, name='admin_why_us'),
    path('admin/why-us/add/', views.admin_why_us_add, name='admin_why_us_add'),
    path('admin/why-us/<int:pk>/edit/', views.admin_why_us_edit, name='admin_why_us_edit'),
    path('admin/why-us/<int:pk>/delete/', views.admin_why_us_delete, name='admin_why_us_delete'),

    # About Section
    path('admin/about/', views.admin_about, name='admin_about'),
    path('admin/about/features/add/', views.admin_about_feature_add, name='admin_about_feature_add'),
    path('admin/about/features/<int:pk>/edit/', views.admin_about_feature_edit, name='admin_about_feature_edit'),
    path('admin/about/features/<int:pk>/delete/', views.admin_about_feature_delete, name='admin_about_feature_delete'),

    # Contact Messages
    path('admin/messages/', views.admin_messages, name='admin_messages'),
    path('admin/messages/<int:pk>/', views.admin_message_detail, name='admin_message_detail'),
    path('admin/messages/<int:pk>/delete/', views.admin_message_delete, name='admin_message_delete'),
    path('admin/messages/<int:pk>/mark-read/', views.admin_message_mark_read, name='admin_message_mark_read'),
    path('admin/messages/mark-all-read/', views.admin_message_mark_all_read, name='admin_message_mark_all_read'),
    path('hero-stats/<int:pk>/toggle/', views.admin_hero_stat_toggle, name='admin_hero_stat_toggle'),
    path('why-us/<int:pk>/toggle/', views.admin_why_us_toggle, name='admin_why_us_toggle'),
        # Videos
    path('admin/videos/', views.admin_videos, name='admin_videos'),
    path('admin/videos/add/', views.admin_video_add, name='admin_video_add'),
    path('admin/videos/<int:pk>/edit/', views.admin_video_edit, name='admin_video_edit'),
    path('admin/videos/<int:pk>/delete/', views.admin_video_delete, name='admin_video_delete'),
    path('admin/videos/<int:pk>/toggle/', views.admin_video_toggle, name='admin_video_toggle'),
]