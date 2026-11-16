import json
import logging
import re
import threading

from datetime import datetime, timedelta
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings as django_settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import (
    ContactForm,
    SiteSettingsForm,
    HeroStatForm,
    ServiceForm,
    AboutSectionForm,
    AboutFeatureForm,
    SectorForm,
    WhyChooseUsForm,
    PartnerForm,
    TestimonialForm,
    VideoForm,
)

from .models import (
    SiteSettings,
    HeroStat,
    Service,
    AboutSection,
    AboutFeature,
    Sector,
    WhyChooseUs,
    Partner,
    Testimonial,
    ContactMessage,
    Video,
)

logger = logging.getLogger(__name__)
def is_staff(user):
    return user.is_staff or user.is_superuser


# ===== AUTHENTICATION =====
from django.contrib.auth import logout

@login_required
@user_passes_test(is_staff)
@require_POST
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')
def admin_login(request):
    from django.contrib.auth import authenticate, login

    if request.user.is_authenticated and is_staff(request.user):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and is_staff(user):
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')

    return render(request, 'core/admin/login.html')


# ===== DASHBOARD =====





@login_required
@user_passes_test(is_staff)
def admin_dashboard(request):
    total_inquiries = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    active_services = Service.objects.filter(is_active=True).count()
    active_sectors = Sector.objects.filter(is_active=True).count()
    active_videos = Video.objects.filter(is_active=True).count()

    # THIS WAS MISSING — recent inquiries in last 7 days
    last_week = timezone.now() - timedelta(days=7)
    recent_inquiries = ContactMessage.objects.filter(created_at__gte=last_week).count()

    sector_stats = ContactMessage.objects.exclude(sector='').values('sector').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    recent_messages = ContactMessage.objects.all()[:10]

    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        day = timezone.now() - timedelta(days=i)
        trend_labels.append(day.strftime('%a'))
        count = ContactMessage.objects.filter(created_at__date=day.date()).count()
        trend_data.append(count)

    context = {
        'total_inquiries': total_inquiries,
        'unread_messages': unread_messages,
        'active_services': active_services,
        'active_sectors': active_sectors,
        'active_videos': active_videos,
        'recent_inquiries': recent_inquiries,  # <-- NOW DEFINED
        'sector_stats': sector_stats,
        'recent_messages': recent_messages,
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_data),
    }
    return render(request, 'core/admin/dashboard.html', context)


# ===== SITE SETTINGS =====

@login_required
@user_passes_test(is_staff)
def admin_settings(request):
    settings_obj = SiteSettings.objects.filter(is_active=True).first()
    if not settings_obj:
        settings_obj = SiteSettings.objects.first()

    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings updated successfully!')
            return redirect('admin_settings')
    else:
        form = SiteSettingsForm(instance=settings_obj)

    return render(request, 'core/admin/form.html', {
        'form': form,
        'title': 'Site Settings',
        'back_url': 'admin_dashboard'
    })


# ===== HERO STATS =====

@login_required
@user_passes_test(is_staff)
def admin_hero_stats(request):
    stats = HeroStat.objects.all()
    return render(request, 'core/admin/list.html', {
        'items': stats,
        'title': 'Hero Stats',
        'add_url': 'admin_hero_stat_add',
        'edit_url': 'admin_hero_stat_edit',
        'delete_url': 'admin_hero_stat_delete',
        'columns': [
            ('Order', 'order'),
            ('Label', 'label'),
            ('Count', 'count'),
            ('Suffix', 'suffix'),
        ]
    })


@login_required
@user_passes_test(is_staff)
def admin_hero_stat_add(request):
    if request.method == 'POST':
        form = HeroStatForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero stat added!')
            return redirect('admin_hero_stats')
    else:
        form = HeroStatForm()
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Add Hero Stat'})


@login_required
@user_passes_test(is_staff)
def admin_hero_stat_edit(request, pk):
    stat = get_object_or_404(HeroStat, pk=pk)
    if request.method == 'POST':
        form = HeroStatForm(request.POST, instance=stat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero stat updated!')
            return redirect('admin_hero_stats')
    else:
        form = HeroStatForm(instance=stat)
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Edit Hero Stat'})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_hero_stat_delete(request, pk):
    stat = get_object_or_404(HeroStat, pk=pk)
    stat.delete()
    messages.success(request, 'Hero stat deleted!')
    return redirect('admin_hero_stats')


# ===== SERVICES =====

@login_required
@user_passes_test(is_staff)
def admin_services(request):
    services = Service.objects.all()
    return render(request, 'core/admin/services.html', {'services': services})


@login_required
@user_passes_test(is_staff)
def admin_service_add(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service added!')
            return redirect('admin_services')
    else:
        form = ServiceForm()
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Add Service'})


@login_required
@user_passes_test(is_staff)
def admin_service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated!')
            return redirect('admin_services')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Edit Service'})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.delete()
    messages.success(request, 'Service deleted!')
    return redirect('admin_services')


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_service_toggle(request, pk):
    service = get_object_or_404(Service, pk=pk)
    service.is_active = not service.is_active
    service.save()
    return JsonResponse({'status': 'success', 'is_active': service.is_active})


# ===== SECTORS =====

@login_required
@user_passes_test(is_staff)
def admin_sectors(request):
    sectors = Sector.objects.all()
    return render(request, 'core/admin/sectors.html', {'sectors': sectors})


@login_required
@user_passes_test(is_staff)
def admin_sector_add(request):
    if request.method == 'POST':
        form = SectorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sector added!')
            return redirect('admin_sectors')
    else:
        form = SectorForm()
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Add Sector'})


@login_required
@user_passes_test(is_staff)
def admin_sector_edit(request, pk):
    sector = get_object_or_404(Sector, pk=pk)
    if request.method == 'POST':
        form = SectorForm(request.POST, request.FILES, instance=sector)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sector updated!')
            return redirect('admin_sectors')
    else:
        form = SectorForm(instance=sector)
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Edit Sector'})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_sector_delete(request, pk):
    sector = get_object_or_404(Sector, pk=pk)
    sector.delete()
    messages.success(request, 'Sector deleted!')
    return redirect('admin_sectors')


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_sector_toggle(request, pk):
    sector = get_object_or_404(Sector, pk=pk)
    sector.is_active = not sector.is_active
    sector.save()
    return JsonResponse({'status': 'success', 'is_active': sector.is_active})


# ===== TESTIMONIALS =====

@login_required
@user_passes_test(is_staff)
def admin_testimonials(request):
    testimonials = Testimonial.objects.all()
    return render(request, 'core/admin/testimonials.html', {'testimonials': testimonials})


@login_required
@user_passes_test(is_staff)
def admin_testimonial_add(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial added!')
            return redirect('admin_testimonials')
    else:
        form = TestimonialForm()
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Add Testimonial'})


@login_required
@user_passes_test(is_staff)
def admin_testimonial_edit(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial updated!')
            return redirect('admin_testimonials')
    else:
        form = TestimonialForm(instance=testimonial)
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Edit Testimonial'})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_testimonial_delete(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    testimonial.delete()
    messages.success(request, 'Testimonial deleted!')
    return redirect('admin_testimonials')


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_testimonial_toggle(request, pk):
    testimonial = get_object_or_404(Testimonial, pk=pk)
    testimonial.is_active = not testimonial.is_active
    testimonial.save()
    return JsonResponse({'status': 'success', 'is_active': testimonial.is_active})


# ===== PARTNERS =====

@login_required
@user_passes_test(is_staff)
def admin_partners(request):
    partners = Partner.objects.all()
    return render(request, 'core/admin/partners.html', {'partners': partners})


@login_required
@user_passes_test(is_staff)
def admin_partner_add(request):
    if request.method == 'POST':
        form = PartnerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partner added!')
            return redirect('admin_partners')
    else:
        form = PartnerForm()
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Add Partner'})


@login_required
@user_passes_test(is_staff)
def admin_partner_edit(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    if request.method == 'POST':
        form = PartnerForm(request.POST, request.FILES, instance=partner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Partner updated!')
            return redirect('admin_partners')
    else:
        form = PartnerForm(instance=partner)
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Edit Partner'})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_partner_delete(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    partner.delete()
    messages.success(request, 'Partner deleted!')
    return redirect('admin_partners')


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_partner_toggle(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    partner.is_active = not partner.is_active
    partner.save()
    return JsonResponse({'status': 'success', 'is_active': partner.is_active})


# ===== WHY CHOOSE US =====

@login_required
@user_passes_test(is_staff)
def admin_why_us(request):
    items = WhyChooseUs.objects.all()
    return render(request, 'core/admin/why_us.html', {'items': items})


@login_required
@user_passes_test(is_staff)
def admin_why_us_add(request):
    if request.method == 'POST':
        form = WhyChooseUsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item added!')
            return redirect('admin_why_us')
    else:
        form = WhyChooseUsForm()
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Add Why Choose Us'})


@login_required
@user_passes_test(is_staff)
def admin_why_us_edit(request, pk):
    item = get_object_or_404(WhyChooseUs, pk=pk)
    if request.method == 'POST':
        form = WhyChooseUsForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated!')
            return redirect('admin_why_us')
    else:
        form = WhyChooseUsForm(instance=item)
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Edit Why Choose Us'})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_why_us_delete(request, pk):
    item = get_object_or_404(WhyChooseUs, pk=pk)
    item.delete()
    messages.success(request, 'Item deleted!')
    return redirect('admin_why_us')


# ===== ABOUT SECTION =====

@login_required
@user_passes_test(is_staff)
def admin_about(request):
    about = AboutSection.objects.filter(is_active=True).first()
    if not about:
        about = AboutSection.objects.first()

    features = about.features.all() if about else []

    if request.method == 'POST':
        form = AboutSectionForm(request.POST, request.FILES, instance=about)
        if form.is_valid():
            form.save()
            messages.success(request, 'About section updated!')
            return redirect('admin_about')
    else:
        form = AboutSectionForm(instance=about)

    return render(request, 'core/admin/about.html', {
        'form': form,
        'features': features,
        'about': about,
    })


@login_required
@user_passes_test(is_staff)
def admin_about_feature_add(request):
    about = AboutSection.objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = AboutFeatureForm(request.POST)
        if form.is_valid():
            feature = form.save(commit=False)
            feature.about = about
            feature.save()
            messages.success(request, 'Feature added!')
            return redirect('admin_about')
    else:
        form = AboutFeatureForm()
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Add About Feature'})


@login_required
@user_passes_test(is_staff)
def admin_about_feature_edit(request, pk):
    feature = get_object_or_404(AboutFeature, pk=pk)
    if request.method == 'POST':
        form = AboutFeatureForm(request.POST, instance=feature)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feature updated!')
            return redirect('admin_about')
    else:
        form = AboutFeatureForm(instance=feature)
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Edit About Feature'})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_about_feature_delete(request, pk):
    feature = get_object_or_404(AboutFeature, pk=pk)
    feature.delete()
    messages.success(request, 'Feature deleted!')
    return redirect('admin_about')


# ===== CONTACT MESSAGES =====

@login_required
@user_passes_test(is_staff)
def admin_messages(request):
    messages_qs = ContactMessage.objects.all()

    status = request.GET.get('status')
    if status == 'unread':
        messages_qs = messages_qs.filter(is_read=False)
    elif status == 'read':
        messages_qs = messages_qs.filter(is_read=True)

    search = request.GET.get('q')
    if search:
        messages_qs = messages_qs.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(message__icontains=search)
        )

    paginator = Paginator(messages_qs, 20)
    page = request.GET.get('page')
    messages_list = paginator.get_page(page)

    return render(request, 'core/admin/messages.html', {
        'messages_list': messages_list,
        'total_count': ContactMessage.objects.count(),
        'unread_count': ContactMessage.objects.filter(is_read=False).count(),
    })


@login_required
@user_passes_test(is_staff)
def admin_message_detail(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    if not message.is_read:
        message.is_read = True
        message.save()
    return render(request, 'core/admin/message_detail.html', {'message': message})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_message_delete(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    message.delete()
    messages.success(request, 'Message deleted!')
    return redirect('admin_messages')


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_message_mark_read(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    message.is_read = True
    message.save()
    return JsonResponse({'status': 'success'})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_message_mark_all_read(request):
    ContactMessage.objects.filter(is_read=False).update(is_read=True)
    messages.success(request, 'All messages marked as read!')
    return redirect('admin_messages')
logger = logging.getLogger(__name__)




# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_site_settings():
    """Get active site settings with fallback."""
    site_settings = SiteSettings.objects.filter(is_active=True).first()
    if not site_settings:
        site_settings = SiteSettings.objects.first()
    return site_settings


def get_home_context(site_settings=None, form=None):
    if site_settings is None:
        site_settings = get_site_settings()

    return {
        'settings': site_settings,
        'hero_stats': HeroStat.objects.filter(is_active=True),
        'services': Service.objects.filter(is_active=True),
        'about': AboutSection.objects.filter(is_active=True).first(),
        'sectors': Sector.objects.filter(is_active=True),
        'why_us': WhyChooseUs.objects.filter(is_active=True),
        'partners': Partner.objects.filter(is_active=True),
        'testimonials': Testimonial.objects.filter(is_active=True),
        'videos': Video.objects.filter(is_active=True),  # <-- ADD THIS
        'form': form or ContactForm(),
    }

def validate_phone_number(phone):
    """Validate phone number format."""
    if not phone:
        return True  # Phone is optional
    # Allow +, digits, spaces, dashes, parentheses
    pattern = r'^[+]?[\d\s\-()]{7,20}$'
    return bool(re.match(pattern, phone))


# =============================================================================
# NOTIFICATION FUNCTIONS (run in background threads)
# =============================================================================

def _send_whatsapp_async(data):
    """Send WhatsApp notification via CallMeBot API (runs in background)."""
    YOUR_PHONE = getattr(django_settings, 'WHATSAPP_PHONE', '')
    YOUR_APIKEY = getattr(django_settings, 'WHATSAPP_API_KEY', '')

    if not YOUR_PHONE or not YOUR_APIKEY:
        logger.warning("WhatsApp credentials not configured in settings")
        return False

    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    sector = data.get('sector', '')
    service = data.get('service', '')
    message_text = data.get('message', '')

    sector_display = sector.replace('_', ' ').title() if sector else 'Not selected'
    service_display = service.replace('_', ' ').title() if service else 'Not selected'

    text = (
        f"🔒 *NEW SECURITY INQUERY*\n\n"
        f"👤 *Name:* {first_name} {last_name}\n"
        f"📧 *Email:* {email}\n"
        f"📱 *Phone:* {phone or 'N/A'}\n"
        f"🏢 *Sector:* {sector_display}\n"
        f"🛡️ *Service:* {service_display}\n"
        f"📝 *Message:* {message_text or 'N/A'}\n\n"
        f"⏰ *Received:* {datetime.now().strftime('%a, %d %b %Y %I:%M %p')}"
    )

    try:
        url = "https://api.callmebot.com/whatsapp.php"
        params = {'phone': YOUR_PHONE, 'text': text, 'apikey': YOUR_APIKEY}
        full_url = f"{url}?{urlencode(params)}"
        response = urlopen(full_url, timeout=10)
        success = response.getcode() == 200
        if success:
            logger.info("WhatsApp notification sent successfully")
        else:
            logger.warning(f"WhatsApp API returned status: {response.getcode()}")
        return success
    except Exception as e:
        logger.error(f"WhatsApp notification error: {e}")
        return False


def _send_email_async(data):
    """Send email notification to admin (runs in background)."""
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    sector = data.get('sector', '')
    service = data.get('service', '')
    message_text = data.get('message', '')

    sector_display = sector.replace('_', ' ').title() if sector else 'Not selected'
    service_display = service.replace('_', ' ').title() if service else 'Not selected'

    subject = f"🔒 New Security Inquiry from {first_name} {last_name}"
    body = (
        f"A new security inquiry has been received.\n\n"
        f"Name: {first_name} {last_name}\n"
        f"Email: {email}\n"
        f"Phone: {phone or 'N/A'}\n"
        f"Sector: {sector_display}\n"
        f"Service: {service_display}\n"
        f"Message: {message_text or 'N/A'}\n\n"
        f"Received: {datetime.now().strftime('%a, %d %b %Y %I:%M %p')}"
    )

    try:
        recipient_list = [getattr(django_settings, 'ADMIN_EMAIL', django_settings.DEFAULT_FROM_EMAIL)]
        send_mail(
            subject=subject,
            message=body,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=True,
        )
        logger.info("Email notification sent successfully")
        return True
    except Exception as e:
        logger.error(f"Email notification error: {e}")
        return False


def send_notifications(data):
    """Send both WhatsApp and email notifications in background threads."""
    # Run WhatsApp in background thread
    wa_thread = threading.Thread(target=_send_whatsapp_async, args=(data,))
    wa_thread.daemon = True
    wa_thread.start()

    # Run email in background thread  
    email_thread = threading.Thread(target=_send_email_async, args=(data,))
    email_thread.daemon = True
    email_thread.start()

    return wa_thread, email_thread


# =============================================================================
# VIEWS
# =============================================================================

def home(request):
    """Home page view with all dynamic content."""
    site_settings = get_site_settings()
    context = get_home_context(site_settings=site_settings)
    return render(request, 'core/index.html', context)


@require_http_methods(["POST"])
def contact_submit(request):
    """Handle contact form submission with validation and notifications."""

    # Rate limiting check (simple session-based)
    session_key = 'last_contact_submit'
    last_submit = request.session.get(session_key)
    now = timezone.now().timestamp()

    if last_submit and (now - last_submit) < 60:  # 60 seconds cooldown
        messages.error(request, '⚠️ Please wait a minute before submitting again.')
        site_settings = get_site_settings()
        context = get_home_context(site_settings=site_settings)
        return render(request, 'core/index.html', context)

    form = ContactForm(request.POST)

    if form.is_valid():
        # Honeypot check (add a hidden field named 'website' in your form)
        if request.POST.get('website'):
            # Bot detected - silently redirect
            logger.warning(f"Honeypot triggered from IP: {request.META.get('REMOTE_ADDR')}")
            return redirect('home')

        # Validate phone format
        phone = form.cleaned_data.get('phone', '')
        if phone and not validate_phone_number(phone):
            form.add_error('phone', 'Please enter a valid phone number.')
            site_settings = get_site_settings()
            context = get_home_context(site_settings=site_settings, form=form)
            return render(request, 'core/index.html', context)

        # Save the form
        try:
            contact_message = form.save()
            logger.info(f"Contact message saved: ID {contact_message.id}")
        except Exception as e:
            logger.error(f"Failed to save contact message: {e}")
            messages.error(request, '⚠️ An error occurred. Please try again later.')
            site_settings = get_site_settings()
            context = get_home_context(site_settings=site_settings, form=form)
            return render(request, 'core/index.html', context)

        # Send notifications in background (non-blocking)
        send_notifications(form.cleaned_data)

        # Set rate limit timestamp
        request.session[session_key] = now

        messages.success(
            request, 
            'Thank you for contacting the Omar Aden campaign. Your message has been received.'
        )
        return redirect('home')

    else:
        # Form has errors - re-render with errors
        messages.error(request, '⚠️ Please correct the errors below.')
        site_settings = get_site_settings()
        context = get_home_context(site_settings=site_settings, form=form)
        return render(request, 'core/index.html', context)


def contact_success(request):
    """Simple success page after contact submission."""
    return render(request, 'core/contact_success.html')


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_hero_stat_toggle(request, pk):
    stat = get_object_or_404(HeroStat, pk=pk)
    stat.is_active = not stat.is_active
    stat.save()
    return JsonResponse({'status': 'success', 'is_active': stat.is_active})

@login_required
@user_passes_test(is_staff)
@require_POST
def admin_why_us_toggle(request, pk):
    item = get_object_or_404(WhyChooseUs, pk=pk)
    item.is_active = not item.is_active
    item.save()
    return JsonResponse({'status': 'success', 'is_active': item.is_active})

# ===== VIDEOS =====

@login_required
@user_passes_test(is_staff)
def admin_videos(request):
    videos = Video.objects.all()
    return render(request, 'core/admin/videos.html', {'videos': videos})


@login_required
@user_passes_test(is_staff)
def admin_video_add(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video added!')
            return redirect('admin_videos')
    else:
        form = VideoForm()
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Add Video'})


@login_required
@user_passes_test(is_staff)
def admin_video_edit(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video updated!')
            return redirect('admin_videos')
    else:
        form = VideoForm(instance=video)
    return render(request, 'core/admin/form.html', {'form': form, 'title': 'Edit Video'})


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_video_delete(request, pk):
    video = get_object_or_404(Video, pk=pk)
    video.delete()
    messages.success(request, 'Video deleted!')
    return redirect('admin_videos')


@login_required
@user_passes_test(is_staff)
@require_POST
def admin_video_toggle(request, pk):
    video = get_object_or_404(Video, pk=pk)
    video.is_active = not video.is_active
    video.save()
    return JsonResponse({'status': 'success', 'is_active': video.is_active})