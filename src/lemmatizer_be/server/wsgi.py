"""WSGI entry for the server.

Can be used with Phusion Passenger
"""

from a2wsgi import ASGIMiddleware

from lemmatizer_be.server.main import app

application = ASGIMiddleware(app)
