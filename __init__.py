from flask import Flask
from view import routes

def createApp():
    app = Flask(__name__)

    app.register_blueprint(routes.blueprint)

    return app