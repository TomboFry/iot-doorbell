import time, pymongo, os
from twilio.rest import TwilioRestClient
from flask import Flask, render_template, request
from pymongo import MongoClient

client = MongoClient()
db = client.doorbell 
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html') 

@app.route('/ding')
def handle_ring():
    ding()
    return "D00T"

@app.route('/settings/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        new_user = User(request.form['name'], request.form['number'], request.form['email'])
        new_user.save()
    return render_template('settings-users.html', users=get_users())

def ding():
    post = {"Time": time.time()}
    db.dings.insert_one(post)
    notify()

def notify():
    return 0;

def get_users():
    users = []
    for user in db.users.find():
        users.append(User(user["Name"],user["Number"],user["Email"]))
    return users

class User(object):
    def __init__(self, name, number, email):
        self.name = name
        self.number = number
        self.email = email

    def save(self):
        post = {"Name": self.name, "Number": self.number, "Email" : self.email}
        db.users.insert_one(post)
    
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
