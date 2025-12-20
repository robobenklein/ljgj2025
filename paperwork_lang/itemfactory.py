

class Item():
    def __init__(self, ID):
        print(f"Creating Item with ID {ID}")
        self.id = ID

class Document(Item):
    def __init__(self, ID):
        super().__init__(ID)
        print("Creating Document")

class Box(Item):
    def __init__(self, ID):
        super().__init__(ID)
        print("Creating Box")

class Cart(Item):
    def __init__(self, ID):
        super().__init__(ID)
        print("Creating Cart")

class ItemFactory():
    constructors = {"doc" : Document, "box" : Box, "cart" : Cart}
    items = {"doc" : [], "box" : [], "cart" : []}

    @classmethod
    def factory(cls, type, itemRange):
        returnIDs = set()

        item_count = len(cls.items[type]);
        if item_count < itemRange[-1] + 1:
            item_constructor = cls.constructors[type]
            items = cls.items[type]
            for i in itemRange:
                items.append(item_constructor(i))
                returnIDs.add(i)
        else:
            for i in itemRange:
                returnIDs.add(i)

        return returnIDs

    @classmethod
    def get_item(cls, type, ID):
        items = cls.items[type]
        if len(items) > ID:
            return items[ID]

        return None
        
    @classmethod
    def clear_items(cls, type):
        cls.items[type].clear()
