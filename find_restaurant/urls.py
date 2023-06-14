"""Defines URL patterns for find_restaurant"""

from django.urls import path
from . import views

app_name = 'find_restaurant'
urlpatterns = [
    # Home page
    path('', views.index, name='index'),
    path('search/', views.search, name='search')
]