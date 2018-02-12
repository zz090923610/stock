class Alarm:
    def __init__(self, type, payload):
        self.type = type  # msg, order
        self.payload = payload

    def emit(self):
        print(self.type, self.payload)
