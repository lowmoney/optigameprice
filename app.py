from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import json
import os

from scrapper import search
#from sendMessage import send

# initalize app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initalize database
db = SQLAlchemy(app)
# intialize marshmellow
ma = Marshmallow(app)

# Game class/model
class Search(db.Model):
    gameName = db.Column(db.String(100), unique=True, primary_key=True)
    shop = db.Column(db.String(100))
    price = db.Column(db.Float)
    link = db.Column(db.String(200))

    def __init__(self, gameName, shop, price, link):
        self.gameName = gameName
        self.shop = shop
        self.price = price
        self.link = link


# user schema
class GameLinkSchema(ma.Schema):
    class Meta:
        fields = ('gameName','link')
class GameSchema(ma.Schema):
    class Meta:
        fields = ('gameName', 'shop', 'price', 'link')

# initiate schema
game_link_schema = GameLinkSchema()
game_schema = GameSchema()

# Search for game
@app.route('/search', methods=['GET'])
def searchGame():
    # Get the search
    key = request.json['key']

    # Get the headers
    link = True
    if request.headers.get('link') is not None:
        link = str(request.headers.get('link')) == "True"
        print(link)

    # See if key is in the data base
    if Search.query.get(key) is None:
        item = search(key)

        # If the game is not in the DataBase then commit to database and return data
        if Search.query.get(item[0]) is None:
            game = Search(item[0], item[1], item[2], item[3])
            db.session.add(game)
            db.session.commit()
            
            # See if we should return just the link or all the data
            if link is True:
                return game_link_schema.jsonify(game)
            else:
                return game_schema(game)
        # Otherwise return from the DataBase
        else:
            return game_link_schema.jsonify(Search.query.get(key))
    # Otherwise see if we want just the link and send the json back
    else:
        if link is True:
            return game_link_schema.jsonify(Search.query.get(key))
        else:
            return game_schema.jsonify(Search.query.get(key))

# link for twilio
@app.route('/sms',methods=['GET'])
def sendMessage():
    # # Get the search key
    # key = request.values.get('Body',None)
    # number = request.values.get('From')

    # if Search.query.get(key) is None:
    #     item = search(key)

    #     if Search.query.get(item[0]) is None:
    #         game = Search(item[0], item[1], item[2], item[3])
    #         db.session.add(game)
    #         db.session.commit()

    #         message = game_link_schema.jsonify(Search.query.get(key))
    #         message = "Found: {} at {} for the lowest price"
    #         message.format(message.json['gameName'],message.json['link'])
    #         send(message,number)
    #     else:
    #         message = game_link_schema.jsonify(Search.query.get(key))
    #         message = "Found: {} at {} for the lowest price"
    #         message.format(message.json['gameName'],message.json['link'])
    #         send(message,number)
    # else:
    #     message = game_link_schema.jsonify(Search.query.get(key))
    #     message = "Found: {} at {} for the lowest price"
    #     message.format(message.json['gameName'],message.json['link'])
    #     send(message,number)
    return("Working on sms")

# Given a game name, redirect the user to the site with the best price
@app.route('/game/<key>',methods=['GET'])
def gameLink(key):
    # Get the search
    fixedKey = key.replace("+"," ")

    # See if key is in the data base
    if Search.query.get(fixedKey) is None:
        item = search(fixedKey)

        # If the game is not in the DataBase then commit to database and return redirect link
        if Search.query.get(item[0]) is None:
            game = Search(item[0], item[1], item[2], item[3])
            db.session.add(game)
            db.session.commit()
            return redirect(item[3], code=302)

        # Otherwise return from the DataBase
        else:
            game = game_link_schema.jsonify(Search.query.get(fixedKey))
            return redirect(game.json['link'], code=301)

    # Otherwise redirect with the link to game
    else:
        game = game_link_schema.jsonify(Search.query.get(fixedKey))
        return redirect(game.json['link'], code=301)

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

# Deal with some errors
@app.errorhandler(404)
def handle_exception(error):
    return "Page not found, Go to: insert link",404

