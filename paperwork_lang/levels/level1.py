
import arcade
import random
import math
import sys

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
        self.completed_once = False

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

                self.time_step = .5 # Tick every 30 frames TODO: Change to button 

            # Then larger random amount and order
            case 1:
                min = 10
                max = 25 + 1
                self.a_doc_count = random.randrange(min, max)
                self.b_doc_count = random.randrange(min, max)
                self.c_doc_count = random.randrange(min, max)
                self.spam_doc_count = random.randrange(min, max)

                self.time_step = .25 # Tick every ~15 frames

            # Finally much larger amount, but seeded random to allow others to compare times
            case 2:
                max = 30
                self.a_doc_count = max
                self.b_doc_count = max
                self.c_doc_count = max
                self.spam_doc_count = max

                self.time_step = 0 # Tick every frame

        self.completion_count = 0
        self.populate_desks()

    def populate_desks(self):
        documentIDs = ItemFactory.factory("doc", range(self.a_doc_count + self.b_doc_count + self.c_doc_count + self.spam_doc_count))

        for i in range(self.a_doc_count):
            ItemFactory.get_item("doc", i).dest = "a"

        for i in range(self.a_doc_count, self.a_doc_count + self.b_doc_count):
            ItemFactory.get_item("doc", i).dest = "b"

        for i in range(self.a_doc_count + self.b_doc_count, self.a_doc_count + self.b_doc_count + self.c_doc_count):
            ItemFactory.get_item("doc", i).dest = "c"

        destinations = ["a", "b", "c"]
        for i in range(self.a_doc_count + self.b_doc_count + self.c_doc_count,  self.a_doc_count + self.b_doc_count + self.c_doc_count + self.spam_doc_count):
            doc = ItemFactory.get_item("doc", i)
            doc.dest = destinations[random.randrange(0, len(destinations))] # The des can still be rand in the last test, should be no diff to the time it takes
            doc.spam = True

        # Randomize the document_ids order
        print(f"ids before {documentIDs}")
        if self.iter_count > 0:
            if self.completed_once == False:
                random.shuffle(documentIDs)
            else:
                random.Random("paperwork").shuffle(documentIDs)

        else:
            # a, a, spam, b, b, spam, c, c, spam,
            # a, a, spam, b, b, spam, c, c, spam,
            # a, b, c
            documentIDs = [
                0, 1, self.a_doc_count + self.b_doc_count + self.c_doc_count      , self.a_doc_count       , self.a_doc_count + 1, self.a_doc_count + self.b_doc_count + self.c_doc_count + 1, self.a_doc_count + self.b_doc_count       , self.a_doc_count + self.b_doc_count + 1, self.a_doc_count + self.b_doc_count + self.c_doc_count + 2,
                2, 3, self.a_doc_count + self.b_doc_count + self.c_doc_count + 3, self.a_doc_count + 2, self.a_doc_count + 3, self.a_doc_count + self.b_doc_count + self.c_doc_count + 4, self.a_doc_count + self.b_doc_count + 2, self.a_doc_count + self.b_doc_count + 3, self.a_doc_count + self.b_doc_count + self.c_doc_count + 5,
                4, self.a_doc_count + 4, self.a_doc_count + self.b_doc_count + 4
            ]

        print(f"ids now {documentIDs}")

        # Tell this desk that when it receives a document it should load level 1
        for interactable_name in self.interactables.keys():
            print(f"Seting up {interactable_name}")
            desk = self.interactables[interactable_name]
            match interactable_name:
                case "desk a":
                    desk.doc_handling = self.document_abc_handler
                    desk.correct_doc_count = 0

                case "desk b":
                    desk.doc_handling = self.document_abc_handler
                    desk.correct_doc_count = 0
                    
                case "desk c":
                    desk.doc_handling = self.document_abc_handler
                    desk.correct_doc_count = 0
                    
                case "desk spambox":
                    desk.doc_handling = self.document_spam_handler
                    desk.correct_doc_count = 0

                case "desk inbox":
                    desk.documents = documentIDs

    def document_abc_handler(level, desk, doc_id):
            desk.documents.remove(doc_id)

            doc = ItemFactory.get_item("doc", doc_id)
            if "desk " + doc.dest == desk.name:
                desk.correct_doc_count += 1
                print(f"{desk.name} got correct document {doc_id}, {desk.correct_doc_count} / {getattr(level, doc.dest + "_doc_count")}")
                if desk.correct_doc_count == getattr(level, doc.dest + "_doc_count"):
                    level.completion_count += 1
                    if level.completion_count == 4: # ABC + Spam desks, could use better way of doing this
                        level.run_completion()
            else:
                print(f"{desk.name} got incorrect document {doc_id} with destination {doc.dest}")
                level.completion_count = -1
                level.run_completion()

            return True

    def document_spam_handler(level, self, doc_id):
        self.documents.remove(doc_id)

        doc = ItemFactory.get_item("doc", doc_id)
        if hasattr(doc, "spam"):
            self.correct_doc_count += 1
            if self.correct_doc_count == level.spam_doc_count:
                level.completion_count += 1
                if level.completion_count == 4: # ABC + Spam desks, could use better way of doing this
                    level.run_completion()
        else:
            print(f"{self.name} got incorrect document {doc_id} with destination {doc.dest}")
            level.completion_count = -1
            level.run_completion()

        return True

    def run_completion(self):
        if self.completion_count == -1:
            print(f"You failed the level, check the console for the first problem encountered.")
            self.iter_count = 0
            self.execution_end()
            self.owner.reset_level() # TODO: This executes too soon
            return
            
        self.iter_count += 1
        if self.iter_count == 3:
            # YAY! Completed!
            print(f"You finished the level in {math.ceil(self.tick_count)} ticks! Can you do better?")
            # TODO: The documents container is not persisting
            print(f"Skipping test 1 and 2 so you can beat your time! Leave and re-open the level to fully reset it. (Level 3 is the same every time, only 2 is random amounts and order)")
            self.execution_end()
            self.owner.reset_level() # TODO: This executes too soon
            self.iter_count = 2
            self.completed_once = True
            return

        self.load()
        self.execution_start()
