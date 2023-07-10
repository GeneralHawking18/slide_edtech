class Authorizer():
    def __init__(self, flow):
        self.flow = flow
        self.url = None
        self.state = None
        self.set()

    def set(self):
        self.url, self.state = self.flow.authorization_url()
    
    def get_url(self):
        return self.url

    def get_state(self):
        return self.state