'''
Main application python script

'''

from flask import Flask, request, g, redirect, url_for
from flask_babel import Babel
from flask_material import Material
from flask_marshmallow import Marshmallow

from config import Config
import json 
import sys
import os

# set up application
app = Flask(__name__)
Material(app)
ma = Marshmallow(app)

app.config.from_object(Config)

# import and register blueprints
from app.blueprints.multilingual import multilingual
app.register_blueprint(multilingual)

# set up babel
babel = Babel(app)


@babel.localeselector
def get_locale():
    if not g.get('lang_code', None):
        g.lang_code = request.accept_languages.best_match(
            app.config['LANGUAGES']) or app.config['LANGUAGES'][0]
    return g.lang_code


@app.route('/')
def home():
    if not g.get('lang_code', None):
        get_locale()
    return redirect(url_for('multilingual.index'))
