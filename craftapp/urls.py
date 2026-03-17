from django.urls import path
from . import views

app_name = 'craftapp'

urlpatterns = [
    # Home / Landing page (all sections: hero, about, resume, services, portfolio, contact)
    path('', views.index, name='index'),

    # About section (anchor-linked on the homepage, but also a standalone endpoint)
    path('about/', views.about, name='about'),

    # Resume section
    path('resume/', views.resume, name='resume'),

    # Services
    path('services/', views.services, name='services'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),

    # Portfolio
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<slug:slug>/', views.portfolio_detail, name='portfolio_detail'),

    # Contact
    path('contact/', views.contact, name='contact'),
    path('contact/send/', views.send_message, name='send_message'),  # POST endpoint for form

    # CV download
    path('download-cv/', views.download_cv, name='download_cv'),
]