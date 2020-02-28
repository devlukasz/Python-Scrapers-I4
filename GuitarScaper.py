from bs4 import BeautifulSoup
import requests
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
import time
import json
import re
url = 'https://www.guitarguitar.co.uk'
description = None
int_priceOff = None
products = []
result = []
productsPage = []
productsRating = None
# getting the crednetials needed to update the firebase database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{'databaseURL': 'https://ctpwebsite-c33ff.firebaseio.com'})
ref = db.reference('ctpwebsite-c33ff')

# making a for loop in order to loop through multiple pages
for page in range(1, 2):
    # grabbing the url with the page
    guitarPage = requests.get('https://www.guitarguitar.co.uk/guitars/electric/page-{}'.format(page)).text
    soup = BeautifulSoup(guitarPage, 'lxml')
    guitars = soup.find_all(class_='col-xs-6 col-sm-4 col-md-4 col-lg-3')
    # for loop for each guitar
    for guitar in guitars:

        title_text = guitar.h3.text.strip()
        # print('Guitar Name: ', title_text)
        price = guitar.find(class_='price bold small').text.strip()
        trim = re.compile(r'[^\d.,]+')
        int_price = trim.sub('', price)
        # print('Guitar Price: ', int_price)

        priceSave = guitar.find('span', {'class': 'price save'})
        if priceSave is not None:
            priceOf = priceSave.text
            trim = re.compile(r'[^\d.,]+')
            int_priceOff = trim.sub('', priceOf)
            # print('Save: ', int_priceOff)
        else:
            pass
            # print("No discount!")

        image = guitar.img.get('src')
        # print('Guitar Image: ', image)

        productLink = guitar.find('a').get('href')
        linkProd = url + productLink
        # print('Link of product', linkProd)
        productsPage.append(linkProd)
        # scraping each products, description and rating value
        for products in productsPage:
            response = requests.get(products)
            soup = BeautifulSoup(response.content, "lxml")
            productsDetails = soup.find("div", {"class": "description-preview"})
            if productsDetails is not None:
                description = productsDetails.text
                # print('product detail: ', description)
            else:
                pass
                # print('none')
            # productsRating = soup.find_all("div", {"class": "col-sm-12"}, "strong")[0].text
            # print(productsRating)
            script = soup.select_one('[type="application/ld+json"]').text
            data = json.loads(script.strip())
            try:
                overall_rating = data['@graph'][2]['aggregateRating']['ratingValue']
                print(overall_rating)
                reviews = [review for review in data['@graph'][2]['review']]  # extract what you want
                print(reviews)
            except:
                overall_rating = "None"
                reviews = ['None']
            time.sleep(0.2)

        # conditional statement in order to make sure that no empty data is sent to products object
        if None not in (title_text, price, image, productLink, description):
            products = {
                'title': title_text,
                'price': int_price,
                'discount': int_priceOff,
                'image': image,
                'link': linkProd,
                'description': description,
                'website' : 'GuitarGuitar',
                'type' : 'Electric',
                'rating': overall_rating,

            }
            # appending the data into results
            result.append(products)
            with open('5.json', 'w') as outfile:
                json.dump(result, outfile, ensure_ascii=False, indent=4, separators=(',', ': '))
            print(result)
            print('--------------------------')
            time.sleep(0.5)
            # updating the firebase database in the child of guitars
            guitars_ref = ref.child('guitars')
            # pushing the data
            guitars_ref.push().set(products)

