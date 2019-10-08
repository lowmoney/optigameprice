from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import desc
import json
import os
import marshmallow_sqlalchemy

from scrapper import search
from sendMessage import send

# initalize app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Make the database with these configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initalize database
db = SQLAlchemy(app)
# intialize marshmellow
ma = Marshmallow(app)

# Game class/model to add the items to database
class Record(db.Model):
    game_name = db.Column(db.String(100), unique=True, primary_key=True)
    hits = db.Column(db.Integer)

    def __init__(self, game_name, hits):
        self.game_name = game_name
        self.hits = hits



# user schema for Marshmallow so it knows what to serialize for jsonify
class GameSchema(ma.Schema):
    class Meta:
        fields = ('game_name', 'hits')

# initiate schemas if we return just one game or the whole database
with app.app_context():
    game_schema = GameSchema()
    game_schemas = GameSchema(many=True)

# Route that searchs for the cheapest price for the game
# Returns json of the name, shop, price, and link if found else returns none 
@app.route('/search', methods=['GET'])
def searchGame():
    key = None

    try:
        key = request.json['key']
    except:
        print("Looked for game name but None was found")
    

    # handle if no key is given
    if key is None:
        return 'No search given in body',428
    
    item = search(key)

    # See if record is in database, if not then add to database
    if Record.query.get(item[0]) is None:
        game = Record(item[0], 1)
        db.session.add(game)
        db.session.commit()
        result = {
            'game':item[0],
            'shop':item[1],
            'price':item[2],
            'link':item[3]
        }
        return jsonify(result), 200
    
    # If it is in database then increase the ammount of hits
    elif Record.query.get(item[0]) is not None:
        oldRecord = Record.query.filter_by(game_name = item[0]).first()
        hit = oldRecord.hits + 1
        game = Record.query.filter_by(game_name=item[0]).first()
        game.hits = hit
        db.session.commit()
        result = {
            'game':item[0],
            'shop':item[1],
            'price':item[2],
            'link':item[3]
        }
        return jsonify(result), 200

    
# Link for the twilio api to send the request with the game name
# Calls the send function from sendMessage to send the game if found
# If not found we return that the game has not populated yet, might not
# be a pc game, or the user spelled something wrong
@app.route('/sms',methods=['GET'])
def sendMessage():

    # Get the search key and the phone number
    key = request.values.get('Body',None)
    number = request.values.get('From')

    # If we cannot find number then return 401 unauthorized. Twilio will give a number
    if number is None:
        abort(401)
    else:
        # Get the game,shop,price,and link
        item = search(key)

        if item[0] is not None:
            message = "Found {} at {} for the lowest price"
            send(message.format(item[0], item[3]),number)

            if Record.query.get(item[0]) is None:
                game = Record(item[0], 1)
                db.session.add(game)
                db.session.commit()
            elif Record.query.get(item[0]) is not None:
                oldRecord = Record.query.filter_by(game_name = item[0]).first()
                hit = oldRecord.hits + 1
                game = Record.query.filter_by(game_name=item[0]).first()
                game.hits = hit
                db.session.commit()

        elif item[0] is None:
            message = '''
            Could not find {} :( This could be because {} has not yet released for the PC or has not populated... but make sure you enter a PC game and/or check the spelling to be sure you searched the right game
            '''
            send(message.format(key,key), number,success=False)

    return "SMS sent", 200

# Given a game name, redirect the user to the site with the best price
@app.route('/game/<key>',methods=['GET'])
def gameLink(key):
    # Get the search
    fixedKey = key.replace("+"," ")

    item = search(fixedKey)

    if Record.query.get(item[0]) is None:
        game = Record(item[0], 1)
        db.session.add(game)
        db.session.commit()

    elif Record.query.get(item[0]) is not None:
        oldRecord = Record.query.filter_by(game_name = item[0]).first()
        hit = oldRecord.hits + 1
        game = Record.query.filter_by(game_name=item[0]).first()
        game.hits = hit
        db.session.commit()

    return redirect(item[3], code=302)

# Hosting the documentation at personal site so redirect people there when going to the site
@app.route("/")
def hello():
    return redirect('https://www.dandyhobbo.com/optigameprice', code=302)

# Check if the server is up
@app.route("/status",methods=['GET'])
def status():
    return "site is up!", 200

# Returns the game and the the amount of hits that game has
# Returns all the games and amount of hits for each
@app.route('/hits/<key>',methods=['GET'])
def giveKey(key):
    if key == "all":
        try:
            all_records = Record.query.all()
            result = game_schemas.dump(all_records)
            return jsonify({'games':result}), 200
        except:
            return "Key not in database", 428
    else:
        try:
            record = Record.query.get(key.format("+"," "))
            return game_schema.jsonify(record), 200
        except:
            return "Key not in database", 428

# Return the most searched game
@app.route('/mostpop',methods=['GET'])
def mostSearched():

    # Get the most popular game from the database
    # Make a schema and seralize
    # Return json object
    record = Record.query.order_by(desc(Record.hits)).limit(1).all()[0]
    return game_schema.jsonify(record), 200

# Return the top three most searched games
@app.route('/topthree', methods=['GET'])
def topThree():
    
    # Get the top three most searched games
    # Run it through the schema
    # Return json object
    most_pop = Record.query.order_by(desc(Record.hits)).limit(3).all()
    result = game_schemas.dump(most_pop)
    return jsonify({'games':result}), 200

# Deal with some errors
@app.errorhandler(404)
def handle_not_found(error):
    return "Page not found, check out the documentation at https://www.dandyhobbo.com/optigameprice", 404

@app.errorhandler(500)
def handle_internal_error(error):
    return "Something went wrong on our side", 500
