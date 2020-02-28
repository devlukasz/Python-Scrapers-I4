from bs4 import BeautifulSoup
import requests
import time
import json
import firebase_admin
import re
from firebase_admin import db
from firebase_admin import credentials
products = []
result = []
productsPage = []
# getting the crednetials needed to update the firebase database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{'databaseURL': 'https://ctpwebsite-c33ff.firebaseio.com'})
ref = db.reference('ctpwebsite-c33ff')
# making a for loop in order to loop through multiple pages
for page in range(1, 5):
    guitarPage = requests.get('https://www.dawsons.co.uk/guitars/acoustic-guitars?p={}'.format(page)).text
    soup = BeautifulSoup(guitarPage, 'lxml')
    guitars = soup.find_all(class_='item')
    # for loop for each guitar
    for guitar in guitars:

        title_text = guitar.h2.text.strip()
        print('Guitar Name: ', title_text)

        price = guitar.find(class_='price').text.strip()
        trim = re.compile(r'[^\d.,]+')
        int_price = trim.sub('', price)
        print('Guitar Price: ', int_price)

        image = guitar.img.get('src')
        print('Guitar Image: ', image)

        productLink = guitar.find('a').get('href')
        print('Link of product', productLink)

        productsPage.append(productLink)
        # scraping each products, description and rating value
        for products in productsPage:
            response = requests.get(products)
            soup = BeautifulSoup(response.content, "lxml")
            productsDetails = soup.find("div", {"class": "short-description"})
            if productsDetails is not None:
                description = productsDetails.text
                print('product detail: ', description)
            else:
                print('none')
            time.sleep(0.2)
        # conditional statement in order to make sure that no empty data is sent to products object
        if None not in (title_text, price, image, productLink, description):
            products = {
                'title': title_text,
                'price': int_price,
                'image': image,
                'link': productLink,
                'description': description,
                'website': 'Dawsons',
                'type': 'Acoustic',

            }
            result.append(products)
            print(result)
            with open('data.json', 'w') as outfile:
                json.dump(result, outfile, ensure_ascii=False, indent=4, separators=(',', ': '))
            print('-------------------')
            time.sleep(0.5)
            # updating the firebase database in the child of guitars
            guitars_ref = ref.child('guitars')
            # pushing the data
            guitars_ref.push().set(products)
