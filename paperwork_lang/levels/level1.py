
import arcade
import random

from ..assets import assets_dir, levels_dir
from ..actor import ChalkActor, Desk
from ..level import ChalkLevel
from ..itemfactory import ItemFactory

class Level1(ChalkLevel):
    """
    Level 1 is just sorting incoming mail.

    Get rid of any spam,

    TAKE desk inbox

    WHEN doc.spam
    MOVE desk spambox

    And sort the rest out to desks ABC.
    """
    level_filename = 'level1.json'

    def setup(self, owner):
        super().setup(owner)

        # level 1 init logic

        self.iter_count = 0

    def load(self):
        super().load()

        for desk in self.interactables.values():
            desk.documents.clear()

        ItemFactory.clear_items("doc")
        
        match self.iter_count:
            # Always starts with: a, a, spam, b, b, spam, c, c, spam, a, a, spam, b, b, spam, c, c, spam, a, b, c
            case 0:
                self.a_doc_count = 5
                self.b_doc_count = 5
                self.c_doc_count = 5
                self.spam_doc_count = 6

                self.time_step = 1 # Tick every ~60 frames

            # Then larger random amount and order
            case 1:
                min = 10
                max = 15 + 1
                self.a_doc_count = random.randrange(min, max)
                self.b_doc_count = random.randrange(min, max)
                self.c_doc_count = random.randrange(min, max)
                self.spam_doc_count = random.randrange(min, max)
                
                self.time_step = .5 # Tick every ~30 frames

            # Finally much larger random amount and order
            case 2:
                min = 50
                max = 100 + 1
                self.a_doc_count = random.randrange(min, max)
                self.b_doc_count = random.randrange(min, max)
                self.c_doc_count = random.randrange(min, max)
                self.spam_doc_count = random.randrange(min, max)

                self.time_step = 0 # Tick every frame

        self.completion_count = 0
        self.populate_desks()

    def populate_desks(self):
        document_ids = ItemFactory.factory("doc", range(self.a_doc_count + self.b_doc_count + self.c_doc_count + self.spam_doc_count))

        for i in range(self.a_doc_count):
            ItemFactory.get_item("doc", i).dest = "A"

        for i in range(self.a_doc_count, self.b_doc_count):
            ItemFactory.get_item("doc", i).dest = "B"

        for i in range(self.b_doc_count, self.c_doc_count):
            ItemFactory.get_item("doc", i).dest = "C"

        desinations = ["A", "B", "C"]
        for i in range(self.c_doc_count, self.spam_doc_count):
            ItemFactory.get_item("doc", i).dest = desinations[random.randrange(0, len(desinations))]
            ItemFactory.get_item("doc", i).spam = True

        # Randomize the document_ids order
        if self.iter_count > 0:
            random.shuffle(document_ids)
        else:
            # a, a, spam, b, b, spam, c, c, spam
            # a, a, spam, b, b, spam, c, c, spam,
            # a, b, c
            document_ids = [
                0, 1, self.c_doc_count, self.a_doc_count, self.a_doc_count + 1, self.c_doc_count + 1, self.b_doc_count, self.b_doc_count + 1,
                2, 3, self.c_doc_count + 2, self.a_doc_count + 2, self.a_doc_count + 3, self.c_doc_count + 3, self.b_doc_count + 2, self.b_doc_count + 3,
                4, self.a_doc_count + 4, self.b_doc_count + 4
            ]

        #document_abc_handler = lambda self, doc_id, level=self:
        def document_abc_handler(self, doc_id, level=self):
            doc = ItemFactory.get_item("doc", doc_id)
            if "desk " + doc.dest == self.name:
                self.correct_doc_count += 1
                if self.correct_doc_count == getattr(level, doc.dest + "_doc_count"):
                    level.completion_count += 1
                    if level.completion_count == 4: # ABC + Spam desks, could use better way of doing this
                        level.run_completion()
                        return
            else:
                print(f"{self.name} got incorrect document {doc_id} with destination {doc.dest}")
                level.completion_count = -1
                level.run_completion()
                return

            self.documents.remove(doc_id)

        # Tell this desk that when it recieves a document it should load level 1
        for interactable_name in self.interactables.keys():
            desk = self.interactables[interactable_name]
            match interactable_name:
                case "desk a":
                    desk.doc_handling = document_abc_handler
                    desk.correct_doc_count = 0

                case "desk b":
                    desk.doc_handling = document_abc_handler
                    desk.correct_doc_count = 0
                    
                case "desk c":
                    desk.doc_handling = document_abc_handler
                    desk.correct_doc_count = 0
                    
                case "spambox":
                    #document_spam_handler = lambda self, doc_id, level=self:
                    def document_spam_handler(self, doc_id, level=self):
                        doc = ItemFactory.get_item("doc", doc_id)
                        if hasattr(doc, "spam"):
                            self.correct_doc_count += 1
                            if self.correct_doc_count == level.spam_doc_count:
                                level.completion_count += 1
                                if level.completion_count == 4: # ABC + Spam desks, could use better way of doing this
                                    level.run_completion()
                                    return
                        else:
                            print(f"{self.name} got incorrect document {doc_id} with destination {doc.dest}")
                            level.completion_count = -1
                            level.run_completion()
                            return

                        self.documents.remove(doc_id)

                    desk.doc_handling = document_spam_handler
                    desk.correct_doc_count = 0

                case "inbox":
                    desk.documents.update(document_ids)

    def run_completion(self):
        if level.completion_count == -1:
            print(f"You failed the level, check the console for the first problem encountered.")
            self.iter_count = 0
            self.owner.reset_level()
            return
            
        self.iter_count += 1
        if self.iter_count == 3:
            # YAY! Completed!
            print(f"You finished the level in {ceil(self.tick_count)} ticks! Can you do better?")
            self.iter_count = 0
            self.owner.reset_level()
            return

        self.load()
