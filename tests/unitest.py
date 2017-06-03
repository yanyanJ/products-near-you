# -*- coding: utf-8 -*-

from server.api import returnRecommendations, haversine, returnShopList
import json
import pytest

def test_returnCorrectDistance():
    dist = haversine(59.3325800, 18.0649000, 59.4325800, 18.098)
    assert (dist == 11276.387753539733) == True
