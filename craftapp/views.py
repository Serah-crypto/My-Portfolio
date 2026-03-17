import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

from .models import (
    Profile,
    Skill,
    Experience,
    Education,
    Certification,
    Service,
    PortfolioItem,
    ContactMessage,
)


# ---------------------------------------------------------------------------
# Helper: build the shared profile context used on multiple pages
# ---------------------------------------------------------------------------

def _get_profile_context():
    """Return the profile and related data shared across most views."""
    profile = Profile.objects.first()  # Single-owner portfolio
    skills = Skill.objects.all().order_by('-percentage')
    return {'profile': profile, 'skills': skills}


# ---------------------------------------------------------------------------
# Main / Landing page
# ---------------------------------------------------------------------------

def index(request):
    """
    Renders the full single-page portfolio (hero → about → resume →
    services → portfolio → contact).
    """
    context = _get_profile_context()

    context.update({
        # Resume
        'experiences': Experience.objects.all().order_by('-start_year'),
        'educations': Education.objects.all().order_by('-start_year'),
        'certifications': Certification.objects.all().order_by('-year'),

        # Services (show all 8 on the homepage)
        'services': Service.objects.all().order_by('order'),
        'featured_service': Service.objects.filter(is_featured=True).first(),

        # Portfolio (show all items; JS handles isotope filtering)
        'portfolio_items': PortfolioItem.objects.all().order_by('-year'),
        'portfolio_categories': PortfolioItem.CATEGORY_CHOICES,

        # Contact info is embedded in the profile model
    })

    return render(request, 'craftivo/index.html', context)


# ---------------------------------------------------------------------------
# About (standalone page / deep-link)
# ---------------------------------------------------------------------------

def about(request):
    """Standalone about page – mirrors the #about section of the homepage."""
    context = _get_profile_context()
    return render(request, 'craftivo/about.html', context)


# ---------------------------------------------------------------------------
# Resume (standalone page / deep-link)
# ---------------------------------------------------------------------------

def resume(request):
    """Standalone resume page – mirrors the #resume section."""
    context = _get_profile_context()
    context.update({
        'experiences': Experience.objects.all().order_by('-start_year'),
        'educations': Education.objects.all().order_by('-start_year'),
        'certifications': Certification.objects.all().order_by('-year'),
    })
    return render(request, 'craftivo/resume.html', context)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

def services(request):
    """Standalone services listing page."""
    context = _get_profile_context()
    context['services'] = Service.objects.all().order_by('order')
    context['featured_service'] = Service.objects.filter(is_featured=True).first()
    return render(request, 'craftivo/services.html', context)


def service_detail(request, slug):
    """Detail page for a single service (maps to service-details.html)."""
    service = get_object_or_404(Service, slug=slug)
    related = Service.objects.exclude(pk=service.pk).order_by('order')[:3]
    context = _get_profile_context()
    context.update({'service': service, 'related_services': related})
    return render(request, 'craftivo/service_detail.html', context)


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------

def portfolio(request):
    """Standalone portfolio page with optional category filter via GET param."""
    category = request.GET.get('category', '')  # e.g. ?category=filter-creative
    items = PortfolioItem.objects.all().order_by('-year')

    if category and category != '*':
        # Strip the leading 'filter-' prefix if present
        cat_key = category.replace('filter-', '')
        items = items.filter(category=cat_key)

    context = _get_profile_context()
    context.update({
        'portfolio_items': items,
        'portfolio_categories': PortfolioItem.CATEGORY_CHOICES,
        'active_category': category,
    })
    return render(request, 'craftivo/portfolio.html', context)


def portfolio_detail(request, slug):
    """Detail page for a single portfolio project."""
    item = get_object_or_404(PortfolioItem, slug=slug)
    related = PortfolioItem.objects.exclude(pk=item.pk).filter(
        category=item.category
    ).order_by('-year')[:3]
    context = _get_profile_context()
    context.update({'item': item, 'related_items': related})
    return render(request, 'craftivo/portfolio_detail.html', context)


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

def contact(request):
    """Standalone contact page."""
    context = _get_profile_context()
    return render(request, 'craftivo/contact.html', context)


@require_POST
def send_message(request):
    """
    Handles the contact form submission.

    Expects POST fields: name, email, subject, message.
    Returns JSON so the front-end PHP-email-form JS replacement can handle it,
    or redirects for non-AJAX submissions.
    """
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    subject = request.POST.get('subject', '').strip()
    body = request.POST.get('message', '').strip()

    # Basic server-side validation
    if not all([name, email, subject, body]):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'All fields are required.'}, status=400)
        messages.error(request, 'All fields are required.')
        return redirect('craftivo:contact')

    # Persist to DB
    ContactMessage.objects.create(
        name=name,
        email=email,
        subject=subject,
        message=body,
    )

    # Send notification email to site owner
    try:
        send_mail(
            subject=f'[Craftivo Contact] {subject}',
            message=f'From: {name} <{email}>\n\n{body}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_RECIPIENT_EMAIL],
            fail_silently=False,
        )
    except Exception:
        # Log the error in production; don't expose it to the user
        pass

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'message': 'Your message has been sent. Thank you!'})

    messages.success(request, 'Your message has been sent. Thank you!')
    return redirect('craftivo:contact')


# ---------------------------------------------------------------------------
# CV download
# ---------------------------------------------------------------------------

def download_cv(request):
    """
    Serves the CV PDF from MEDIA_ROOT.
    Expects the file path to be stored on the Profile model as `cv_file`.
    """
    profile = Profile.objects.first()
    if not profile or not profile.cv_file:
        raise Http404('CV not available.')

    file_path = profile.cv_file.path
    if not os.path.exists(file_path):
        raise Http404('CV file not found on disk.')

    response = FileResponse(
        open(file_path, 'rb'),
        content_type='application/pdf',
    )
    response['Content-Disposition'] = f'attachment; filename="cv_{profile.name.replace(" ", "_")}.pdf"'
    return response