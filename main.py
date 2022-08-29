import csv
from datetime import datetime
import json
from os.path import exists
import re
import sys

from bs4 import BeautifulSoup
import requests
import pandas as pd


wishlist_url = "https://www.amazon.co.uk/hz/wishlist/ls/2F7TLWIU7S1IG/"

added_list = []
item_list = []
price_list = []
id_list = []
counter = 0
seen = {}

def get_wishlist(url:str) -> object:
    """
    Retrieve the wishlist from the specified URL.

    Params:
    -------
    url: str
        The URL for the wishlist to be processed.

    Returns:
    -------
    object: A BS4 object representing the HTML from the wishlist page.
    """
    response = requests.get(url)
    page_html = response.text
    
    soup = BeautifulSoup(page_html, 'html.parser')
    return soup


def get_items(page:object):
    """
    Get all of the wish list items from the page.

    Params:
    -------
    page: object
        The page object holding the items.
    """
    for match in page.find_all('a', id=re.compile('itemName_')):
        item = match.string.strip()
        item_list.append(item)


def get_prices_and_ids(page:object):
    """
    Retrieves the price and ID from data attributes.

    Params:
    -------
    page: object
        The page holding the items.
    """
    for match in page.find_all('li', class_='g-item-sortable'):
        price = match.attrs['data-price']
        price_list.append(float(price))
        
        json_data = json.loads(match.attrs['data-reposition-action-params'])
        # Will be something like "ASIN:B095PV5G87|A1F83G8C2ARO7P"
        amazon_id = json_data['itemExternalId'].split(":")[1].split("|")[0]
        id_list.append(amazon_id)

    for added in page.find_all('span', id=re.compile('itemAddedDate_')):
        added_list.append(added.text.split('Item added')[1].strip())


def get_paginator(page:object):
    """
    Returns the paginator for the Wishlist data.

    Params:
    -------
    page: object
        The page holding the items.
    """
    paginator = None
    
    # Find the paginator
    if page.find('div', {'AmazonID': 'endOfListMarker'}) is None:
        # If the end tag doesn't exist, continue
        for match in page.find_all('input', class_='showMoreUrl'):
            paginator = f'https://www.amazon.co.uk{match.attrs["value"]}'
    
    return paginator


def get_all(url):
    global counter
    counter = counter + 1
    print(f'Getting page {counter} - {url}')

    seen[url] = True

    soup = get_wishlist(url)
    
    get_items(soup)
    
    get_prices_and_ids(soup)
    
    paginator = get_paginator(soup)
    if paginator is not None and paginator not in seen:
        get_all(paginator)


today = datetime.today().strftime('%Y%m%d')
todays_filename = f'data/{today}.csv'
if exists(todays_filename):
    print('Already run today, won\'t run again.')
    sys.exit(0)

get_all(wishlist_url)

all_items = zip(id_list, item_list, price_list, added_list)
new_prices = pd.DataFrame(list(all_items), columns = ['AmazonID', 'Name', 'Price', 'Added'])

new_prices.to_csv(todays_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)
