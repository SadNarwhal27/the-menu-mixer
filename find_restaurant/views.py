from django.shortcuts import render, redirect
from nearby_search import Google

# Might have to create a separate landing and search page

def index(request):
    """The home page for The Menu Mixer"""
    restaurant = Google().nearby_search('mt pleasant, mi')
    context = restaurant
    return render(request, 'find_restaurant/index.html', context)

def search(request):
    return render(request, 'find_restaurant/search.html')