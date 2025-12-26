
from ..level import ChalkLevel

from .level1 import Level1

class MenuLevel(ChalkLevel):
    """
    The menu level is a special case where the player can issue commands directly to the Actor in real time to move around.

    I don't think any other level is going to do something like this.
    
    Current flow: Move to Desk C, Take from Desk C, Move to Desk A/B, Drop to select level A/B 
    """
    level_filename = 'menu1.json'

    def setup(self, owner):
        super().setup(owner)
        self.player = self.actors["player"]

        # Tell this desk that when it receives a document it should load level 1
        self.item_factory.get_item('desk', 'B').doc_handling = self.load_level_1

    def load(self):
        super().load()

    def execution_step(self):
        super().execution_step()

    def load_level_1(self, desk, doc_id):
        # TODO: this instantly loads could be bad if things need to finish? (Like this desk)
        self.owner.add_level(Level1)
        return True
