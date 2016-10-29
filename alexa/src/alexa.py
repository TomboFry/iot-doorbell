import logging

from flask import Flask
from flask_ask import Ask, request, session, question, statement


app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

def RingBell():
    return;

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
    RingBell()
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


if __name__ == '__main__':
    app.run(debug=True)


