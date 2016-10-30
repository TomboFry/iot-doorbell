from flask_ask import Ask, session, question, statement
import logging

class Alexa(object):
    """docstring for Alexa"""
    def __init__(self, app):
        super(Alexa, self).__init__()
        self.app = app
        self.ask = Ask(self.app, "/alexa")
        logging.getLogger('flask_ask').setLevel(logging.DEBUG)

        def LastRing():
            last = stats_latest_ding();
            unit = 'seconds';
            if last > 60:
                last = math.floor(float(last)/60);
                unit = 'minutes';

            if last > 60:
                last = math.floor(last/60);
                unit = 'hours';

            return str(int(round(last))) + ' ' + unit;

        def SetNotificationLevel(level):
            urgency_set(level);
            return level;

        @self.ask.launch
        def launch():
            speech_text = 'Welcome to Dr Doorbell'
            return question(speech_text).simple_card('', speech_text)


        @self.ask.intent('RingDoorBellIntent')
        def RingDoorBellIntent():
            ding()
            speech_text = ''
            return statement(speech_text).simple_card('', speech_text)


        @self.ask.intent('LastRingIntent')
        def LastRingIntent():
            speech_text = 'The bell wast last rung ' + LastRing() + ' ago'
            return statement(speech_text).simple_card('', speech_text)

        @self.ask.intent('NotificationLevelIntent',mapping={'level' : 'NotificationLevel'})
        def NotificationLevelIntent(level):
            speech_text = SetNotificationLevel(level);
            return statement(speech_text).simple_card('', speech_text)


        @self.ask.session_ended
        def session_ended():
            return "", 200
