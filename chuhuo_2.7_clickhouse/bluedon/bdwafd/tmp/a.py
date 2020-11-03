class a(object):
    def __init__(self):
        self.b = self
    def __del__(self):
        print '__del__'
