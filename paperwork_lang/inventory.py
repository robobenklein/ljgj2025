

class ActorInventory():
    def __init__(self):
        self.item_map = {"doc" : set(), "box" : set(), "cart" : set() }
        pass

    def add_item(self, params):
        if params.parcel_type != "any":
            if params.parcel_identifier != None:
                self.item_map[params.parcel_type].add(params.parcel_identifier)
            else:
                raise ValueError("add_item was passed an empty item ID, this is not allowed!")
        else:
            raise ValueError("add_item was passed 'any' for the item type, this is not allowed!")

    # Passing in 'any' will remove the first item, looking in this order: Doc, Box, Cart
    def remove_item(self, params):
        if params.parcel_type != "any":
            self.item_map[params.parcel_type].remove(params.parcel_identifier)
        else: 
            # Find the first set that has items
            for key in self.item_map:
                print(f"Remove Any Key: {key}")
                if len(self.item_map[key]):
                    item_set.pop()
                    return

    # Passing in 'any' will check if the inventory is not empty
    def contains_item(self, params):
        if params.parcel_type != "any":
            return params.parcel_identifier in self.item_map[params.parcel_type]
        else: 
            # Find the first set that has items
            for key in self.item_map:
                if len(self.item_map[key]):
                    return True

            return False
