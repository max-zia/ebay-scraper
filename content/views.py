from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import SearchForm
from .models import Search
# imports for webscrape
import requests
from selenium import webdriver
import time
from lxml import html

def index(request):
    if request.method != 'POST':
        form = SearchForm()
    else:
        form = SearchForm(data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('content:search'))            

    return render(request, 'content/index.html', {'form': form})

def search(request):
    # get search term from database and parse data
    usersearch = Search.objects.all().order_by('-id')[0]
    term = usersearch.searchterm

    # implement search and webscrape
    url = 'https://www.ebay.co.uk'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=options)
    browser.get(url)
    inputBox = browser.find_element_by_id('gh-ac')
    inputBox.send_keys(term)
    inputBox.submit()
    time.sleep(3)
    r = requests.get(browser.current_url)
    tree = html.fromstring(r.content)
    price_list = tree.xpath('//*[contains(@class,"lvprice prc")]/span/text()')
    name_list = tree.xpath('//*[contains(@class, "vip")]/text()')

    # initialise context data
    context = {'term': term, 'prices': price_list, 'names': name_list}
    return render(request, 'content/search.html', context)