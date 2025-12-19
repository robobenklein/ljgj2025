
import arcade

from ..assets import assets_dir, levels_dir
from ..actor import ChalkActor, Desk
from ..level import ChalkLevel
from .level1 import Level1

class PlayerActor(ChalkActor):
    def __init__(self):
        super().__init__(
            assets_dir / "char1.png",
            # assets_dir / "chalk-desk1.png",
            scale=1/4,
        )

class MenuLevel(ChalkLevel):
    """
    The menu level is a special case where the player can issue commands directly to the Actor in real time to move around.

    I don't think any other level is going to do something like this.
    
    Current flow: Move to Desk C, Take from Desk C, Move to Desk A/B, Drop to select level A/B 
    """
    level_filename = 'menu1.json'

    def setup(self, owner):
        super().setup(owner)
        self.player = self.actors[0]

        # TODO: Do we need to construct the documents too?
        self.interactables["desk a"].documents.add(1) # Normally this would be a range of documents
        
        # Tell this desk that when it recieves a document it should load level 1
        self.interactables["desk b"].doc_handling = self.load_level_1

    def load(self):
        super().load()
        
        for desk in self.interactables.values():
            desk.documents.clear()

        self.interactables["desk a"].documents.add(1)

    def execution_step(self):
        super().execution_step()

    def load_level_1(self, doc_id):
        # TODO: this instantly loads could be bad if things need to finish? (Like this desk)
        self.owner.add_level(Level1)
        return True
