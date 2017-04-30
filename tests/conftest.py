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

@pytest.mark.parametrize(
    'reqOk', [
        {'lat': '59.3325800', 'lng': '18.0649000', 'radius':'500.0', 'tags':'casual','count':'2'},
        {'lat': '59.3325800', 'lng': '18.0649000', 'radius':'500.0', 'tags':'','count':'2'},
        {'lat': '0', 'lng': '0', 'radius':'0', 'tags':'','count':'2'}
    ]
)
def test_returnOkWithValidParams(client, reqOk):
    req = {'lat': '59.3325800', 'lng': '18.0649000', 'radius':'500.0', 'tags':'casual','count':'2'}
    response= client.post('/search', data = req)
    assert response.status_code == 200

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
def test_returnBadRequestWhenParameterIsMissingOrEmpty(client, reqBad):
    req = {'lat': '', 'lng': '18.0649000', 'radius':'500', 'tags':'casual','count':'2'}
    response= client.post('/search', data = req)
    assert response.status_code == 400

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
