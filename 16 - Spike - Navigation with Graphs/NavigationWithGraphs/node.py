class Node(object):
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0
        
        self.neighbors = []

    def __eq__(self, other):
        if other is None:
            return False
        return self.position == other.position
    
    def __hash__(self):
        return hash(self.position)
    