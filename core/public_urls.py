"""
URLs publiques nécessitant une API key
Ces endpoints sont accessibles sans authentification JWT mais nécessitent une API key valide
"""
from django.urls import path
from contacts.views import ContactSubmitPublicView
from projects.views import ProjectPublicView, ProjectPublicDetailView

urlpatterns = [
    # Contact form submission
    path('contact/submit/', ContactSubmitPublicView.as_view(), name='public-contact-submit'),

    # Projects (read-only)
    path('projects/', ProjectPublicView.as_view(), name='public-projects-list'),
    path('projects/<slug:slug>/', ProjectPublicDetailView.as_view(), name='public-project-detail'),
]
