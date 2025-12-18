
import arcade

from ..assets import assets_dir, levels_dir
from ..actor import ChalkActor, Desk
from ..level import ChalkLevel


class Level1(ChalkLevel):
    """
    Level 1 is just sorting incoming mail.

    Get rid of any spam,

    WHEN doc.spam
    MOVE desk spambox

    And sort the rest out to desks ABC.
    """
    level_filename = 'level1.json'

    def setup(self):
        super().setup()

        # level 1 init logic
