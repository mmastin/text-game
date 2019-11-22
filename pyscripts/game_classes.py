import random

class room:
    def __init__(self, location):
        self.location = location
        self.occupied = False
        self.name = None
        
    def room_name_generator(self):
        first_words = ['Firey', 'Whispering', 'Ancient', 'Musty',
        'Bloody', 'Treasure', 'Green', 'Babbling',
        'Creaky', 'Freezing', 'Dank', 'Mysterious', 
        'Magical', 'Wandering', 'Deathly']
        second_words = ['Hobgloblin', 'Orc', 'Centaur', 'Dwarf',
        'Goliath', 'Gnome', 'Dragon', 'Emerald',
        'Wizard', 'Hearthstone', 'Warlock', 'Aragorn',
        'Gollum', 'Gimli', 'Saruman', 'Balrog',
        'Cellar', 'Chamber', 'Wight']
        rand_name = random.choice(first_words) + ' ' + random.choice(second_words)
        self.name = rand_name

class gameMap:
    def __init__(self):
        self.map = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.rooms = []
    
    def generate_rooms(self):
        for x in range(len(self.map)):
            r = room(x)
            r.room_name_generator()
            self.rooms.append(r)


class Player:
    def __init__(self, location, id_):
        self.location = location
        self.id_ = id_
        self.health = 100
        self.strength = 20