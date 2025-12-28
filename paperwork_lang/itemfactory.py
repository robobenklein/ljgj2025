
import arcade

from .assets import assets_dir

class Item():
    def __init__(self, ID, item_tobj):
        print(f"Creating Item with ID {ID}")
        self.id = ID

        for property_name in item_tobj.properties:
            setattr(self, property_name, item_tobj.properties[property_name])

class Document(Item):
    def __init__(self, ID, item_tobj):
        print("Creating Document")
        super().__init__(ID, item_tobj)

class Box(Item, arcade.Sprite):
    def __init__(self, ID, item_tobj, **kargs):
        print("Creating Box")
        super().__init__(ID, item_tobj)

class Cart(Item, arcade.Sprite):
    def __init__(self, ID, item_tobj, **kargs):
        print("Creating Cart")
        super().__init__(ID, item_tobj)

class Tutorial(Item, arcade.BasicSprite):
    def __init__(self, ID, item_tobj, **kargs):
        print("Creating Tutorial")
        super().__init__(ID, item_tobj)
        arcade.BasicSprite.__init__(self,
            arcade.texture.default_texture_cache.load_or_get_texture(assets_dir / "chalk-cpu-acronym.png"),
            scale=1/4,
        )

        self.position = arcade.LRBT(
                min(x[0] for x in item_tobj.shape),
                max(x[0] for x in item_tobj.shape),
                min(x[1] for x in item_tobj.shape),
                max(x[1] for x in item_tobj.shape),
            ).center
        self._hit_box = arcade.hitbox.HitBox([(0,0), (0,0)])

        self.level = kargs['level']
        if hasattr(self.level, 'tutorial_sprites') == False: # Not all levels will have tutorial, so dont make part of the base level
            self.level.tutorial_sprites = self.level.add_sprite_list('Tutorials')
            self.level.interactable_sprites.append(self.level.tutorial_sprites)

        self.level.tutorial_sprites.append(self)

        self.name = item_tobj.name.title().replace('{}', f"{ID}")

        fontSize = 24
        self.name_sprite = arcade.create_text_sprite(self.name, arcade.color.WHITE, fontSize)
        self.name_sprite.hit_box = arcade.hitbox.HitBox([(0,0), (0,0)])

        padding = 12
        self.name_sprite.position = (self.position[0], self.position[1] + self.height / 2 + padding)
        self.level.text_sprites.append(self.name_sprite)
    
    def load(self, item_tobj):
        pass # TODO: If we decide to hide them after view, we could re-visible them

    def interact(self):
        messageBox = arcade.gui.UIMessageBox(width=400, height=400, message_text=self.message, title=self.name, buttons=("Close",))
        self.level.owner.camera_world_space.add(messageBox)

class DocumentSpawner(Item):
    def __init__(self, ID, item_tobj, **kargs):
        print("Creating Document Spawner")
        super().__init__(ID, item_tobj)
        self.owner = kargs['level']

    def load(self, item_tobj):
        area = arcade.LRBT(
                min(x[0] for x in item_tobj.shape),
                max(x[0] for x in item_tobj.shape),
                min(x[1] for x in item_tobj.shape),
                max(x[1] for x in item_tobj.shape),
            )
        overlap = arcade.get_sprites_in_rect(area, self.owner.desk_sprites)

        # TODO: Add a way to control turning printing on/off
        print(f"Spawning {self.count} Documents for Desk {overlap[0]}") # TODO: Overlap may not be a desk (sprite instead)
        
        class DocObj(): pass

        doc_tobjs = []
        for i in range(self.count):
            tobj = DocObj()
            tobj.type = 'doc'
            tobj.properties = item_tobj.properties.copy()
            tobj.properties.pop('count') # Docs don't need that
            doc_tobjs.append(tobj)

        newDocs = self.owner.item_factory.factory(doc_tobjs)
        if newDocs == None or len(newDocs) != self.count:
            print(f"{overlap[0].name} failed to add docks!")

        overlap[0].documents.extend(newDocs)

# TODO: move this and the tutorial to separate files? (Would need to move the base item too to avoid circular include for the tutorial)
class Desk(arcade.BasicSprite):
    def __init__(self, tobj, **kargs):
        super().__init__(
            arcade.texture.default_texture_cache.load_or_get_texture(assets_dir / "chalk-desk1.png"),
            scale=1/4,
        )
        level = kargs['level']
        
        # original data from loading the Tiled object
        self._tobj = tobj

        self.name = tobj.name.lower()
        print(f"desk name {self.name}")

        # determine position based on the object bounds:
        self.bounds = arcade.LRBT(
            min(x[0] for x in tobj.shape),
            max(x[0] for x in tobj.shape),
            min(x[1] for x in tobj.shape),
            max(x[1] for x in tobj.shape),
        )
        self.position = self.bounds.center

        for property_name in tobj.properties:
            setattr(self, property_name, tobj.properties[property_name])

        self.documents = []
        self.doc_handling = lambda *_: None

        level.desk_sprites.append(self)

        fontSize = 24
        if len(tobj.name) == len("desk ."):
            self.name_sprite = arcade.create_text_sprite(f"{tobj.name.title()}", arcade.color.WHITE, fontSize) # Desk A, Desk B, Desk C, etc.
        else:
            self.name_sprite = arcade.create_text_sprite(f"{tobj.name.split(' ')[1].title()}", arcade.color.WHITE, fontSize) # Remove the 'desk' from the name as it's longer than just a letter

        self.name_sprite.hit_box = arcade.hitbox.HitBox([(0,0), (0,0)])

        padding = (2, 12)
        self.name_sprite.position = (self.position[0] + padding[0], self.position[1] + padding[1])
        level.text_sprites.append(self.name_sprite)

    def load(self, tobj):
        print(f"Clearing docs for desk: {self.name}")
        self.documents.clear()

    def tick(self):
        # TODO: Don't tick when we don't need to?

        stopTicking = True
        tempList = self.documents # In case the doc IDs are removed in the handler
        for doc in tempList:
            if self.doc_handling(self, doc) == False:
                stopTicking = False

        pass

    def interact(self, params):
        match params.__class__.__name__:
            case "InsTake":
                if params.parcel_identifier == None:
                    if len(self.documents) :
                        ID = next(iter(self.documents))
                        self.documents.remove(ID)
                        return ID
                elif params.parcel_identifier in self.documents:
                    print(f"{self.name} removing {params.parcel_type} {params.parcel_identifier}")
                    self.documents.remove(params.parcel_identifier)
                    return params.parcel_identifier

            case "InsDrop":
                # TODO: Start ticking (when it's not on by default)
                print(f"{self.name} adding {params.parcel_type} {params.parcel_identifier}")
                self.documents.append(params.parcel_identifier)
                return params.parcel_identifier
            case _:
                raise NotImplementedError(params.__class__.__name__)

        return -1
            
# TODO: Not really just an 'item' factory anymore
class ItemFactory():
    def __init__(self):
        self.constructors = {'doc' : Document, 'box' : Box, 'cart' : Cart, 'tutorial' : Tutorial, 'desk' : Desk, 'doc_spawner' : DocumentSpawner} # Loaded in order left->right
        self.items = {}

    class Obj(): 
        def __init__(self, properties):
            self.properties = properties
    
    def factory(self, item_data_list, **kargs):
        returnIDs = []

        for item_tobj in item_data_list:
            if hasattr(item_tobj, 'name') == False or item_tobj.name.endswith("{}"): # These will be populated with IDs instead of names
                if item_tobj.type not in self.items:
                    self.items[item_tobj.type] = []

                item_list = self.items[item_tobj.type]
                ID = len(item_list)
                item_list.append(self.constructors[item_tobj.type](ID, item_tobj, **kargs))
                returnIDs.append(ID)
            else:
                if item_tobj.type not in self.items:
                    self.items[item_tobj.type] = {}
                
                ID = item_tobj.name.replace(item_tobj.type, '').lstrip().lower()

                item_dict = self.items[item_tobj.type]
                item_dict[ID] = self.constructors[item_tobj.type](item_tobj, **kargs)
                returnIDs.append(ID)

        return returnIDs
    
    def factory_clone(self, type, item_range, clone = None):
        returnIDs = []

        if type not in self.items:
            self.items[type] = []

        items = self.items[type]
        item_count = len(items)
        if item_count > item_range[0]:
            for i in range(item_range[0], item_count):
                returnIDs.append(i)

        if item_count < item_range[-1] + 1:
            item_constructor = self.constructors[type]
            
            if clone == None:
                clone = ItemFactory.Obj([])
            
            for i in item_range:
                items.append(item_constructor(i, clone))
                returnIDs.append(i)

        return returnIDs

    def load_items(self, item_data_lists):
        for item_type in self.constructors:
            if item_type in self.items: # May have not been created yet because they are dynamic (so created on load, like docs)
                pluralType = f"{item_type}s"
                print(f"Loading {pluralType}")
                if pluralType in item_data_lists:
                    item_container = self.items[item_type]
                    if type(item_container) is list:
                        iterator = iter(item_container)
                        for item_tobj in item_data_lists[pluralType]:
                            next(iterator).load(item_tobj)
                    else:
                        for item_tobj in item_data_lists[pluralType]:
                            ID = item_tobj.name.replace(item_tobj.type, '').lstrip().lower()
                            item_container[ID].load(item_tobj)
                else:
                    self.items[item_type].clear() # These must be dynamic data so clear them now and they will be populated later

    def get_item_count(self, type):
        return len(self.items[type])

    def get_item(self, item_type, ID):
        item_container = self.items[item_type]
        if type(item_container) is list:
            intID = int(ID)
            if len(item_container) > intID:
                return item_container[intID]
        else:
            lowerID = ID.lower()
            if lowerID in item_container:
                return item_container[lowerID]

        return None

    def get_items(self, type):
        return self.items[type]

    def clear_items(self, type):
        self.items[type].clear()
