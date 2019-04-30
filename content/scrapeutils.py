import requests
from selenium import webdriver
from lxml import html

class Main():

    def implement_search(browser, website, input_id, searchterm):
        # visits a url, locates an input box, and submits a searchterm.
        # the result can be stored using lxml and requests. this is
        # implemented in GetData.tree_of_current_page().
        Nav.go_to_url(browser, website)
        inputBox = Nav.get_input_box(browser, input_id)
        Nav.submit_input_box(inputBox, searchterm)

    def get_browser():
        # initialise headless mode, which means that the browser
        # will not launch visibly. then initialise the browser.
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        browser = webdriver.Chrome(chrome_options=options)
        return browser

class Nav():

    def go_to_url(browser, url):
        # using selenium.webdriver, the headless browser navigates
        # to the url specified by the user.
        browser.get(url)

    def get_input_box(browser, input_id):
        input_box = browser.find_element_by_id(input_id)
        return input_box
    
    def submit_input_box(input_box, searchterm):
        input_box.send_keys(searchterm)
        input_box.submit()

class GetData():

    def tree_of_current_page(browser):
        # pull DOM and other info from current url. use lxml.html
        # to parse into tree-like structure which can then be searched
        # using xpath queries (see get_ebay_data(), etc.).
        r = requests.get(browser.current_url)
        tree = html.fromstring(r.content)
        return tree 

    def get_ebay_data(ebay_tree, xpath_query_array):
        # retrieve items from html page by calling an array of xpaths.
        # here, (a) two price lists are created, (b) logic is applied
        # to merge the two lists, (c) a name list is created, and (d)
        # the image src and link href attributes are obtained.
        # finally, zip() iterates over the 4 lists, creating a
        # list of dictionaries to store the data. 
        ebay_data = []

        price_single = ebay_tree.xpath(xpath_query_array[0])
        price_range = ebay_tree.xpath(xpath_query_array[1]) 
        prices = GetData.process_ebay_price(price_single, price_range)
        names = ebay_tree.xpath(xpath_query_array[2])
        imgs = ebay_tree.xpath(xpath_query_array[3])
        links = ebay_tree.xpath(xpath_query_array[4])

        for price, name, img, link in zip(prices, names, imgs, links):
            ebay_data.append({
                'price': price,
                'name': name,
                'img': img,
                'link': link,
            })

        return ebay_data

    def process_ebay_price(single_array, range_array):
        # If a product on one of ebay's pages has a range for a price
        # rather than an int (e.g., 100-150 vs 100), then a proper
        # list of prices needs to be created to format ranges like
        # (inta + ' to ' + intb). if there isn't a range array, then you 
        # don't need to merge the two arrays together.
        processed_array = []
        if range_array:
            # set flags for while loop
            x = 0 # track progression through the single_array
            y = 0 # track progression through the range_array
            while x < len(single_array):
                # if the list item doesn't contain '£', then we've run
                # into a range price on ebay. therefore, skip two list
                # items (since range prices come in pairs), and take the
                # next two values from the range_array, which constitute
                # the range price pair.
                if '£' in single_array[x]:
                    processed_array.append(single_array[x])
                    x += 1
                else:
                    processed_array.append(
                        range_array[y] + ' to ' + range_array[y+1]
                    )
                    y += 2
                    x += 2
        else:
            # some product lists on ebay might not have range prices,
            # in which case the correct price list is simply the one
            # containing all the single prices.
            processed_array = single_array
        return processed_array

