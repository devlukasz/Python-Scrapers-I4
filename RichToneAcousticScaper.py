from bs4 import BeautifulSoup
import requests
import time
import json
import firebase_admin
import re
from firebase_admin import db
from firebase_admin import credentials
url = 'https://www.richtonemusic.co.uk'
products = []
result = []
productsPage = []
titleOff = None
priceOf = None
imageOf = None
linkProd = None
description = None
# getting the crednetials needed to update the firebase database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{'databaseURL': 'https://ctpwebsite-c33ff.firebaseio.com'})
ref = db.reference('ctpwebsite-c33ff')
# making a for loop in order to loop through multiple pages

for page in range(1, 3):
    guitarPage = requests.get('https://www.richtonemusic.co.uk/search/?range=2&page={}'.format(page)).text
    soup = BeautifulSoup(guitarPage, 'lxml')
    # row = soup.find(class_='row products flex-row')
    guitars = soup.find_all(class_='grid__item')
    # for loop for each guitar
    for guitar in guitars:
        # lots of conditional statments to avoid crashes caused by un-familiar web architecture
        title_text = guitar.find(class_='block__title')
        if title_text is not None:
            titleOff = title_text.get_text().strip()
            print('Guitar Name: ', titleOff)
        else:
            print("No Title")

        price = guitar.find(class_='block__price')
        if price is not None:
            priceOf = price.get_text().strip()
            trim = re.compile(r'[^\d.,]+')
            int_priceOff = trim.sub('', priceOf)
            print('Guitar Price: ', int_priceOff)
        else:
            print("No price found")

        image = guitar.find('img', {"class": "block_img lazyload"})
        if image is not None:
            imageOf = image.get('data-src')
            print('Guitar Image: ', imageOf)
        else:
            print("No Image Found")

        productLink = guitar.find('a').get('href')
        if productLink is not None:
            linkProd = url + productLink
            print('Link of product', linkProd)
        else:
            print('No link detected')

        productsPage.append(linkProd)
        # scraping each products, description and rating value
        for products in productsPage:
            response = requests.get(products)
            soup = BeautifulSoup(response.content, "lxml")
            productsDetails = soup.find("div", {"class": "pageCopy prd_desc"})
            if productsDetails is not None:
                description = productsDetails.text
                print('product detail: ', description)
            else:
                print('none')
            time.sleep(0.2)
        # conditional statement in order to make sure that no empty data is sent to products object
        if None not in (titleOff, price, imageOf, linkProd, description):
            products = {
                'title': titleOff,
                'price': int_priceOff,
                'image': imageOf,
                'link': linkProd,
                'description': description,
                'website': 'Richtonemusic',
                'type': 'Acoustic',
            }
            result.append(products)
            print(result)
            with open('data8.json', 'w') as outfile:
                json.dump(result, outfile, ensure_ascii=False, indent=4, separators=(',', ': '))
            print(result)
            print('--------------------------')
            time.sleep(0.5)
            # updating the firebase database in the child of guitars
            guitars_ref = ref.child('guitars')
            # pushing the data
            guitars_ref.push().set(products)
