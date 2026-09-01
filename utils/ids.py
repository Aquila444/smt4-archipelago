class IdGenerator:

    def __init__(self):
        self.counter = 0

    def get_new_id(self):
        self.counter += 1
        return self.counter
