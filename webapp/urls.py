from django.conf.urls import url
from django_redirects_file import load_redirects
from views import MaasTemplateFinder, custom_404, custom_500

urlpatterns = load_redirects()

# Standard patterns
urlpatterns += [
    url(r'^(?P<template>.*)/?$', MaasTemplateFinder.as_view()),  # Fenchurch
]

# Error handlers
handler404 = custom_404
handler500 = custom_500
