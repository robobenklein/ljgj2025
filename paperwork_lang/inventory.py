

class ActorInventory():
    def __init__(self):
        self.item_map = {"doc" : set(), "box" : set(), "cart" : set()}
        pass

    def add_item(self, params):
        if params.parcel_type != "any":
            if params.parcel_identifier != None:
                self.item_map[params.parcel_type].add(params.parcel_identifier)
            else:
                raise ValueError("add_item was passed an empty item ID, this is not allowed!")
        else:
            raise ValueError("add_item was passed 'any' for the item type, this is not allowed!")

    # Passing in 'any' or no ID will remove the last item, looking in this order: Doc, Box, Cart
    def remove_item(self, params):
        if params.parcel_type != "any":
            if params.parcel_identifier != None:
                self.item_map[params.parcel_type].remove(params.parcel_identifier)
            else:
                self.item_map[params.parcel_type].popitem()
        else: 
            # Find the first set that has items and remove the last one
            for key in self.item_map:
                print(f"Remove Any Key: {key}")
                if len(self.item_map[key]):
                    item_set.popitem()
                    return

    # Passing in 'any' or no ID will check if the inventory is not empty
    def contains_item(self, params):
        if params.parcel_type != "any":
            if params.parcel_identifier != None:
                return params.parcel_identifier in self.item_map[params.parcel_type]
            else:
                return len(self.item_map[params.parcel_type]) > 0
        else: 
            # Find the first set that has items
            for key in self.item_map:
                if len(self.item_map[key]):
                    return True

            return False

    def get_first_itemID(self, item_type):
        if item_type != "any":
            items = self.item_map[item_type]
            if len(items):
                for ID in items:
                    return ID
        else: 
            # Find the first set that has items
            for key in self.item_map:
                ID = self.get_last_itemID(key)
                if ID >= 0:
                    return ID

        return -1
