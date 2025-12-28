
from ..level import ChalkLevel

class TestLevel(ChalkLevel):
    """
    For controlled running of tests
    """
    level_filename = 'testing.json'

    def setup(self, owner):
        super().setup(owner)
        self.player = self.actors["tester"]

    def load(self):
        super().load()

    def execution_step(self):
        super().execution_step()
