# -*- coding: utf-8 -*-

from server.api import returnRecommendations, haversine
import json
import pytest

@pytest.mark.parametrize(
'lat,lng, radius, tags, count', [
('59.3325800', '18.0649000', '500.0','casual','10'),
('59.3325800', '18.0649000', '500.0','','20'),
('59.3325800', '18.0649000', '2000.0','casual, tops, women','50')
])
def test_returnProductsWithinRaidusWithinCountWithTags(lat, lng, radius,tags,count):
    products = returnRecommendations(lat, lng, radius,tags,count)
    if products is not None:
        prodList = json.loads(products)
        assert len(prodList) <= int(count)
        for prod in prodList:
            assert haversine(float (prod['shop']['lat']) , float(prod['shop']['lng']), 59.3325800,18.0649000)  <= float(radius)
            if tags:
                assert (prod['tag'] in tags) == True
