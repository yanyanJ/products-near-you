# -*- coding: utf-8 -*-

import json
import functools
import os
import sys

import pytest
from flask import Flask
from werkzeug.test import EnvironBuilder

# Set up the path to import from `server`.
root = os.path.join(os.path.dirname(__file__))
package = os.path.join(root, '..')
sys.path.insert(0, os.path.abspath(package))

from server.app import create_app

class TestResponseClass(Flask.response_class):
    @property
    def json(self):
        return json.loads(self.data)

Flask.response_class = TestResponseClass

def test_returnOkWithValidParams(client):
    req = {'lat': '59.3325800', 'lng': '18.0649000', 'radius':'100.0', 'tags':'tops','count':'1'}
    response= client.post('/search', data = req)
    assert response.status_code == 200
    data = json.loads(response.get_data())
    assert len(data['products']) == 1
    assert data['products'][0]['tag'] == 'tops'
    assert float(data['products'][0]['shop']['lat']) == 59.33310561456153
    assert float(data['products'][0]['shop']['lng']) == 18.06501795312943

@pytest.mark.parametrize(
    'reqBad', [
        {'lat': '', 'lng': '18.0649000', 'radius':'500.0', 'tags':'casual','count':'2'},
        {'lat': '59.3325800', 'lng': '', 'radius':'500.0', 'tags':'casual','count':'2'},
        {'lat': '59.3325800', 'lng': '18.0649000', 'radius':'', 'tags':'casual','count':'2'},
        {'lat': '59.3325800', 'lng': '18.0649000', 'radius':'500.0', 'tags':'casual','count':''},
        {'lng': '18.0649000', 'radius':'500.0', 'tags':'casual','count':'2'},
        {'lat': '59.3325800', 'radius':'500.0', 'tags':'casual','count':'2'},
        {'lat': '59.3325800', 'lng': '18.0649000', 'tags':'casual','count':'2'},
        {'lat': '59.3325800', 'lng': '18.0649000', 'radius':'500.0', 'tags':'casual'}
    ]
)
def test_returnBadRequestWhenLatIsMissingOrEmpty(client, reqBad):
    response= client.post('/search', data = reqBad)
    assert response.status_code == 400
    data = json.loads(response.get_data())
    assert data['message'] == 'Bad Request: Lat, lng, count and raidus cannot be empty or null and must be of numerial type.'

def humanize_werkzeug_client(client_method):
    """Wraps a `werkzeug` client method (the client provided by `Flask`) to make
    it easier to use in tests.

    """
    @functools.wraps(client_method)
    def wrapper(url, **kwargs):
        # Always set the content type to `application/json`.
        kwargs.setdefault('headers', {}).update({
            'content-type': 'application/x-www-form-urlencoded'
        })

        kwargs['buffered'] = True

        return client_method(url, **kwargs)

    return wrapper


@pytest.fixture(scope='session', autouse=True)
def app(request):
    app = create_app({
        'TESTING': True
    })

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app

@pytest.fixture(scope='function')
def client(app, request):
    return app.test_client()


@pytest.fixture(scope='function')
def get(client):
    return humanize_werkzeug_client(client.get)
