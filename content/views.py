from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SearchForm
from .models import Search
# imports for webscrape
import time
from .scrapeutils import *

def index(request):
    # save form and redirect after valid post to the server.
    if request.method != 'POST':
        form = SearchForm()
    else:
        form = SearchForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('content:search'))            

    return render(request, 'content/index.html', {'form': form})

def search(request):
    # get the search term last entered into the database. this is the
    # term the user just posted in content/index.html
    usersearch = Search.objects.all().order_by('-id')[0]
    term = usersearch.searchterm

    # implement search using content/scrapeutils.py
    browser = Main.get_browser()
    Main.implement_search(browser, 'https://www.ebay.co.uk', 'gh-ac', term)
    time.sleep(0.5)

    # implement webscrape using content/scrapeutils.py
    tree = GetData.tree_of_current_page(browser)
    ebay_data = GetData.get_ebay_data(
        tree,
        [
            # xpath queries for ebay prices, names, imgs, and links
            '//*[contains(@class,"lvprice prc")]/span[last()]/text()',
            '//*[contains(@class,"prRange")]/text()',
            '//*[contains(@class, "vip")]/text()',
            '//*[contains(@class, "lvpicinner full-width picW")]/a/img/@src',
            '//*[contains(@class, "vip")]/@href',
        ]
    )

    # initialise context data
    context = {
        'term': term, 
        'ebay_data': ebay_data,
    }
    
    return render(request, 'content/search.html', context)