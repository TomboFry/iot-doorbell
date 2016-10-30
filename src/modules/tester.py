from module import DingPlugin

class Tester(DingPlugin):
    def __init__(self):
        super(Tester, self).__init__()

    def init(self, users):
        config = {
            "api_key": "",
            "email": ""
        }
        for user in users:
            db.users.modules.tester.insert_one(config)
