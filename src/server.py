#!/usr/bin/env python
from twilio.rest import TwilioRestClient

import time, pymongo, os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import math
import json

import module
from alexa import Alexa

HOST = os.environ.get('SERVER_ADDRESS') or '0.0.0.0'
PORT = int(os.environ.get('SERVER_PORT') or '8080')
MHOST = os.environ.get('MONGODB_ADDRESS') or 'localhost'
MPORT = int(os.environ.get('MONGODB_PORT') or '27017')

client = MongoClient(MHOST, MPORT)
db = client.doorbell
app = Flask(__name__)
modules = None
class Phone:
    """docstring for Twilio"""
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

text = Phone()

@app.route('/ding', methods=['POST'])
def handle_ring():
    ding()
    return "D00T"

@app.route("/")
def page_dashboard():
    init_users();
    return render_template('dashboard.html') 

@app.route("/stats")
def page_stats():
    return render_template('stats.html')

@app.route("/stats/latest_ding_friendly")
def friendly_ding():
    return LastRing();

@app.route("/stats/latest_ding")
def stats_latest_ding():
    data = db.dings.find().sort("Time", -1).limit(1)
    if data != None:
        latest = int(time.time()) - data[0]["Time"]
        return str(latest)

@app.route('/stats/count/<string:inLast>', methods=['GET'])
def dingcount(inLast):
    since = time.time()-int(inLast)
    data = db.dings.find({"Time": {"$gte": since}}).count();
    return str(data);

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
    if data.get('priorities'):
        priorities =  {"low": data['priorities']['low'], "medium": data['priorities']['medium'], "high": data['priorities']['high']}
        user = User(data['name'], data['number'], data['email'], data['key'], priorities) 
    else:
        user = User(data['name'], data['number'], data['email'], data['key'])
    user.save()
    return ""

@app.route('/settings/users/modules/<string:user_id>')
def page_settings_user_modules(user_id):
    return render_template('settings-user-module.html', user=get_user(user_id))

@app.route('/settings/users/delete', methods=['POST'])
def delete_user():
    data = request.get_json()
    print data
    db.users.remove( { "_id" : ObjectId(data['key']) } )
    return ""

@app.route('/settings/notifications')
def page_settings_notifications():
    return render_template('settings-notifications.html')

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

@app.route('/settings/init')
def init_users():
    if str(db.users.find().count()) == '0':
        user = User("Dan","012100000","dan@me.lol");
        user.save();
        user = User("Jack", "012331232", "jack@me.lol");
        user.save();
        user = User("Tom","012100003240","tom@me.lol");
        user.save();
        user = User("Joe", "012234331232", "joe@me.lol");
        user.save();
    return "";

def ding():
    post = {"Time": time.time()}
    db.dings.insert_one(post)

    import pusher

    pusher_client = pusher.Pusher(
            app_id='264785',
            key='c710991e5ca26dd51147',
            secret='6cbe822c7c795fbd8135',
            ssl=True
            )

    pusher_client.trigger('test_channel', 'my_event', {'message': 'hello world'})

    notify()

def notify():
    map(lambda u: u.notify(urgency_get()), get_users())

def get_users():
    users = []
    for user in db.users.find():
        users.append(User(user["Name"],user["Number"],user["Email"],user["_id"],user["priorities"]))
    return users

def get_user(user_id):
    user = db.users.find_one( { "_id": ObjectId(user_id) } )
    return { "name": user["Name"], "number": user["Number"], "email": user["Email"], "key": user_id }

@app.route('/settings/users/getuser/<string:user_id>', methods=['GET'])
def get_user_json(user_id):
    return json.dump(get_user(user_id))

class User(object):
    def __init__(self, name, number, email, key=None, priorities = {"low": ['twilio'], "medium": ['twilio'], "high": ['twilio']}):
        self.name = name
        self.number = number
        self.email = email
        self.id = key
        self.priorities = priorities

    def save(self):
        post = {"Name": self.name, "Number": self.number, "Email" : self.email, "priorities" : self.priorities}
        if self.id == None:
            db.users.insert_one(post)
        else:
            db.users.update( { "_id" : ObjectId(self.id) }, post )      

    def notify(self, urgency):
        print "blah"
        notifiers = None
        if urgency == 'low':
            notifiers = self.priorities['low'] 
        elif urgency == 'high':
            notifiers = self.priorities['high']
        elif urgency == 'medium':
            notifiers = self.priorities['medium']

        if 'twilio' in notifiers:
            text.text("doorbell rang", self.number)

if __name__ == "__main__":
    modules = module.load_modules("modules", [])
    Alexa(app);
    app.run(host=HOST, port=PORT)




