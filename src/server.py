import time, pymongo, os
from twilio.rest import TwilioRestClient
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

client = MongoClient()
db = client.doorbell 
app = Flask(__name__)

@app.route('/ding')
def handle_ring():
    ding()
    return "D00T"

@app.route("/")
def page_dashboard():
    return render_template('dashboard.html') 

@app.route("/stats")
def page_stats():
    return render_template('stats.html') 

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
    return redirect(url_for('users'))

@app.route('/settings/users/update', methods=['POST'])
def update_user():
    user = User(request.form['name'], request.form['number'], request.form['email'], request.form['key'])
    user.save()
    return redirect(url_for('users'))

@app.route('/settings/users/delete', methods=['POST'])
def delete_user():
    db.users.remove( { "_id" : request.form['key'] } )
    return redirect(url_for('users'))

@app.route('/settings/notifications')
def page_settings_notifications():
    return render_template('settings-notifications.html')

def ding():
    post = {"Time": time.time()}
    db.dings.insert_one(post)
    notify()

def notify():
    return 0;

def get_users():
    users = []
    for user in db.users.find():
        users.append(User(user["Name"],user["Number"],user["Email"],user["_id"]))
    return users

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
            db.users.update( { "_id" : self.key }, post )      

    
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

if __name__ == "__main__":
    app.run()
