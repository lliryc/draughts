
class Movement:

    def __init__(self, position):
        self.score = 0
        self.steps = [position]

    def add(self, movement):
        self.score = self.score + movement.score
        self.steps = self.steps + movement.steps[1:]
