# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, jsonify, request
from math import radians, cos, sin, asin, sqrt
import pandas as pd

api = Blueprint('api', __name__)

def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)

products = pd.read_csv('data/products.csv')
shops = pd.read_csv('data/shops.csv')
taggings = pd.read_csv('data/taggings.csv')
tags = pd.read_csv('data/tags.csv')

def findAvailableProds():
    availableProducts = products.loc[products['quantity']>0]
    availableProducts= pd.merge(left= availableProducts, right= shops, how='left', left_on='shop_id', right_on='id')
    result = availableProducts[['id_x','shop_id','popularity','title','name','lat','lng']]
    return result

def haversine(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    return 2 * asin(sqrt(a)) * 6371000

def returnShopList(lat, lng, r):
    shopList=[]
    for shop in shops.itertuples():
        distance = haversine(shop.lat,shop.lng,float(lat),float(lng))
        if distance <= float(r):
            shopList.append(shop.id)
    return shopList

def returnProdsInShops(shoplist):
    availableProducts = findAvailableProds()
    productsInShop = availableProducts[availableProducts['shop_id'].isin(shoplist)]
    return productsInShop

def mergeShopsInfo(productsInShop):
    productsInShop['shop']=productsInShop.apply(lambda row: {"name":row['name'],"lat":row['lat'], "lng":row['lng']}, axis=1)
    mergedProds = productsInShop[['shop_id','title','popularity','shop']]
    return mergedProds

def returnTaggedShops(keywords):
    if keywords:
        wordlist=keywords.split(',')
        mentionedTags = tags[tags['tag'].isin(wordlist)]
        mergedTaggings = pd.merge(left= mentionedTags, right= taggings, how='left', left_on='id', right_on='tag_id')
        taggedShops = mergedTaggings['shop_id'].tolist()
    else:
        taggedShops = taggings['shop_id'].tolist()
    return taggedShops

def returnRecommendations(lat, lng, r, keywords, n):
    shoplist = returnShopList(lat, lng, r)
    prodsInShops = returnProdsInShops(shoplist)
    mergedProds = mergeShopsInfo(prodsInShops)
    taggedShoplist = returnTaggedShops(keywords)
    recommendation = mergedProds[mergedProds['shop_id'].isin(taggedShoplist)]
    topN = recommendation.sort_values(by='popularity', ascending=0).head(int(n))
    return topN


@api.route('/search', methods=['POST'])
#def search():
def search():
    lat = request.form['lat']
    lng = request.form['lng']
    r = request.form['radius']
    keywords = request.form['tags']
    n = request.form['count']
    recommendation = returnRecommendations(lat=lat, lng=lng, r=r, keywords=keywords, n=n)
    return jsonify({'products': recommendation.to_json(orient='records')})