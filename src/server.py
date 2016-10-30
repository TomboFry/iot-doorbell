import time, pymongo, os
from twilio.rest import TwilioRestClient
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId


client = MongoClient()

db = client.doorbell
app = Flask(__name__)

@app.route('/ding', methods=['POST'])
def handle_ring():
    ding()
    return "D00T"

@app.route("/")
def page_dashboard():
    return render_template('dashboard.html') 

@app.route("/stats")
def page_stats():
    return render_template('stats.html')

@app.route("/stats/latest_ding")
def stats_latest_ding():
    data = db.dings.find().sort("Time", -1).limit(1)
    if data != None:
        latest = int(time.time()) - data[0]["Time"]
        return str(latest)

@app.route('/settings')
def page_settings():
    return render_template('settings.html')

@app.route('/settings/users', methods=['GET', 'POST'])
def page_settings_users():
    return render_template('settings-users.html', users=get_users())

@app.route('/settings/users/add', methods=['POST'])
def add_user():
    new_user = User(request.form['name'], request.form['number'], request.form['email'])
    new_user.save()
    return redirect(url_for('page_settings_users'))

@app.route('/settings/users/update', methods=['POST'])
def update_user():
    data = request.get_json()
    user = User(data['name'], data['number'], data['email'], data['key'])
    user.save()
    return ""

@app.route('/settings/users/delete', methods=['POST'])
def delete_user():
    data = request.get_json()
    print data
    db.users.remove( { "_id" : ObjectId(data['key']) } )
    return ""

@app.route('/settings/notifications')
def page_settings_notifications():
    return render_template('settings-notifications.html')

@app.route('/stats/count/<string:inLast>', methods=['GET'])
def dingcount(inLast):
    since = time.time()-int(inLast)
    data = db.dings.find({"Time": {"$gte": since}}).count();
    return str(data);

@app.route('/settings/urgency/<string:urgency>', methods=['GET'])
def urgency_set(urgency):
    if urgency == "low" or urgency == "medium" or urgency == "high":
        db.urgency.update({}, {"status": urgency}, upsert=True)
    return redirect(url_for('page_dashboard'))

@app.route('/settings/urgency', methods=['GET'])
def urgency_get():
    data = db.urgency.find_one()
    if data != None:
        return data["status"]
    else:
        db.urgency.update({}, {"status" : "medium"},upsert=True)
        urgency_get()
        return ""

def ding():
    post = {"Time": time.time()}
    db.dings.insert_one(post)
    notify()

def notify():
    return 0

def get_users():
    users = []
    for user in db.users.find():
        users.append(User(user["Name"],user["Number"],user["Email"],user["_id"]))
    return users

@app.route('/settings/users/getuser/<string:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.users.find_one( { "_id": ObjectId(user_id) } )
    return '{ "name": "' + user["Name"] + '", "number": "' + user["Number"] + '", "email": "' + user["Email"] + '", "key": "' + user_id + '" }'

class User(object):
    def __init__(self, name, number, email, key=None):
        self.name = name
        self.number = number
        self.email = email
        self.id = key

    def save(self):
        post = {"Name": self.name, "Number": self.number, "Email" : self.email}
        if self.id == None:
            db.users.insert_one(post)
        else:
            db.users.update( { "_id" : self.id }, post )      

class Phone(object):
    def __init__(self):
        (twilio_number, twilio_account_sid, twilio_auth_token) = self.get_config()
        self.number = twilio_number
        self.client = TwilioRestClient(twilio_account_sid, twilio_auth_token)

    def text(self, body, to):
        self.client.messages.create(body = body, to = to, from_ = self.number)

    def get_config(self):
        twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        twilio_number = os.environ.get('TWILIO_NUMBER')

        if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
            print("twilio config not used")
        return (twilio_number, twilio_account_sid, twilio_auth_token)



# alexa stuff
from flask_ask import Ask, session, question, statement
import logging

ask = Ask(app, "/alexa")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

def LastRing():
    last = "never"
    return last;

def SetNotificationLevel(level):
    return level;

@ask.launch
def launch():
    speech_text = 'Welcome to Dr Doorbell'
    return question(speech_text).simple_card('', speech_text)


@ask.intent('RingDoorBellIntent')
def RingDoorBellIntent():
    ding()
    speech_text = ''
    return statement(speech_text).simple_card('', speech_text)


@ask.intent('LastRingIntent')
def LastRingIntent():
    speech_text = 'The bell wast last rung at ' + LastRing()
    return statement(speech_text).simple_card('', speech_text)

@ask.intent('NotificationLevelIntent',mapping={'level' : 'NotificationLevel'})
def NotificationLevelIntent(level):
    speech_text = SetNotificationLevel(level);
    return statement(speech_text).simple_card('', speech_text)


@ask.session_ended
def session_ended():
    return "", 200


if __name__ == "__main__":
    app.run()
