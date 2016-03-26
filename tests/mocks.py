from game import Game

class SerializerMock(object):
    def __init__(self):
        pass
    def is_block(self, idx, idy):
        return False
    def load_block(self, idx, idy, world):
        return None
    def save_block(self, block):
        pass

class StatusBarMock(object):
    def __init__(self):
        pass
    def draw(self):
        pass


class HeadlessGame(Game):
    # TODO move things out of init for Game
    def __init__(self):
        self.update_view()

