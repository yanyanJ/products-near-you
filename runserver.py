# -*- coding: utf-8 -*-

from server.app import create_app
from flask_cors import CORS,cross_origin

app = create_app()
CORS(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
