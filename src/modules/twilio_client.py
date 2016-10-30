from module import DingPlugin
from twilio.rest import TwilioRestClient

class Twilio(DingPlugin):
    """docstring for Twilio"""
    def __init__(self, app):
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
