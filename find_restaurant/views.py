from django.shortcuts import render, redirect
from nearby_search import Google

# Might have to create a separate landing and search page

def index(request):
    """The home page for The Menu Mixer"""
    restaurant = Google().nearby_search('mt pleasant, mi')
    context = {'restaurant': restaurant} # Will need to create entries for each field (ex. Name)
    return render(request, 'find_restaurant/index.html', context)