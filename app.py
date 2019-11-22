from flask import Flask, render_template
from flask_socketio import SocketIO
import random
from pyscripts.game_classes import *
import eventlet
import gevent

gmap = gameMap()
gmap.generate_rooms()
num_players = 0
players = []
potions = ["(^)", "(+)", "(!)"]
bad_norths = [x for x in range(0, 10)]
bad_souths = [x for x in range(90, 100)]
bad_easts = [x for x in range(9, 100, 10)]
bad_wests = [x for x in range(0, 100, 10)]
possible_directions = {"n": -10, "s": 10, "e": 1, "w": -1}
deaths = 0

# Create flask app
app = Flask(__name__)
# Set app's secret key
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
# Wrap Socketio around app
socketio = SocketIO(app)

# Start Screen
@app.route('/')
def start():
    return render_template('start.html', data = deaths)

# Game route
@app.route('/game')
def game():
    return render_template('game.html')


# Callback function to aid in debugging
def messageReceived(data, methods=['GET', 'POST']):
    print(f'Data recieved: {data}')

# Game socket (Runs when socket recieves data)
@socketio.on('game-socket')
# Function that takes in recived data, GET and POST are nessesary to recieve and send data
def custom_event(data, methods=['GET', 'POST']):
    messageReceived(data)
    # Runs when client first connects
    if data["data"] == "Connection made with client":
        # allow num players to be referenced here
        global num_players
        # create an id for the new player 
        id_ = num_players + 1
        # checks map for available spots
        available = [index for index in range(len(gmap.map)) if gmap.map[index] == 0]
        try:
            # Set a random spawn location
            position = random.choice(available)
        except:
            # if room is filled, send user back to start screen
            return render_template('game.html')
        #create player object with position and id
        player = Player(position, id_)
        # append new player to players
        players.append(player)
        # Update gamemap to include player
        gmap.map[player.location] = player.id_
        # Increment amount of players by 1
        num_players += 1
        message = " has joined the dungeon"
        # Create the data that will be sent back(map cords and players id)
        data = {"data": gmap.map, "player": player.id_, "message": message}
        # sent client data
        return socketio.emit('my response', data)
    # Runs if client is already connected
    else:
        # Grab the players id from data recieved
        id_ = int(data["player"])
        if players[id_-1].health <= 0:
            return render_template('end.html')
        # Runs if user sent a message
        if data["message"] != '':
            data = {"data": gmap.map, "player": data["player"], "message": data["message"]}
            return socketio.emit('my response', data)
        # Runs if user is moving
        else:
            # Check direction inputed
            direction = data["data"].lower()
            # Check players current position on map
            position = gmap.map.index(id_)
            # run if direction is valid
            if direction in possible_directions:
                # checks map for available spots
                available = [index for index in range(len(gmap.map)) if gmap.map[index] == 0]
                chance = random.randint(0, 100)
                random_spawn = random.choice(available)
                if chance <= 20:
                    gmap.map[random_spawn] = "(+)"
                elif (chance > 20) and (chance <= 40):
                    gmap.map[random_spawn] = "(^)"
                elif (chance > 40) and (chance <= 60):
                    gmap.map[random_spawn] = "(!)"
                elif (chance == 99):
                    gmap.map[random_spawn] = "\***/"
                else:
                    pass
                # create new position
                new_position = position + possible_directions[direction]
                # runs new position is on the map
                if (new_position >= 0) and (new_position <= 99):
                    # Runs if room has an enemy
                    if (new_position not in available) and (gmap.map[new_position] not in potions):
                        # grabs the enemies id
                        enemy_id = gmap.map[new_position]
                        # decreses enemies health by player strength
                        players[enemy_id -1].health -= players[id_-1].strength
                        enemy_health = players[enemy_id-1].health
                        # runs if the enemy died
                        if players[enemy_id-1].health <= 0:
                            # players current room is empty
                            gmap.map[position] = 0
                            # player takes enemies room
                            gmap.map[new_position] = id_
                            global deaths
                            deaths += 1
                            event = f" killed Player {enemy_id}"
                            data = {"data": gmap.map, "player": id_, "event": event}
                            return socketio.emit('my response', data)
                        # runs if they are alive
                        else:
                            # grabs enemy position
                            enemy_position = new_position
                            # all random choices
                            flee_to = random.choice(available)
                            # check if it works
                            gmap.map[position] = 0
                            gmap.map[enemy_position] = id_
                            gmap.map[flee_to] = enemy_id
                            event = f" attacked Player {enemy_id}, causing them to flee with {enemy_health} health remaining"
                            data = {"data": gmap.map, "player": id_, "attack": 1, "event": event}
                            return socketio.emit('my response', data)
                    # Runs if health potion was found
                    elif (gmap.map[new_position] == "(+)"):
                        gmap.map[position] = 0
                        gmap.map[new_position] = id_
                        players[id_ - 1].health += 20
                        event = f" found a health potion. Their health has risen to {players[id_ -1].health}"
                        data = {"data" : gmap.map, "player": id_, "event": event}
                        return socketio.emit('my response', data)
                    elif (gmap.map[new_position] == "(^)"):
                        gmap.map[position] = 0
                        gmap.map[new_position] = id_
                        players[id_ - 1].strength += 20
                        event = f" found a strength potion. Their strength has risen to {players[id_ -1].strength}"
                        data = {"data" : gmap.map, "player": id_, "event": event}
                        return socketio.emit('my response', data)
                    elif (gmap.map[new_position] == "(!)"):
                        gmap.map[position] = 0
                        gmap.map[new_position] = id_
                        players[id_ - 1].health -= 20
                        event = f" stepped on a trap. Their remaining health is {players[id_ -1].health}"
                        data = {"data" : gmap.map, "player": id_, "event": event}
                        return socketio.emit('my response', data)
                     # Runs if room is empty
                    else:
                        # if the direction the user chose was north, and they are on the top of the map
                        if (direction == "n") and (position in bad_norths):
                            # return current map
                            event = " attempted to escape the dungeon"
                            data = {"data": gmap.map, "player": id_, "event": event}
                            return socketio.emit('my response', data)
                        # if the direction is south and they are on the bottom of the map
                        elif (direction == "s") and (position in bad_souths):
                            event = " attempted to escape the dungeon"
                            data = {"data": gmap.map, "player": id_, "event": event}
                            return socketio.emit('my response', data)
                        # if the direction they chose was west and they are on the left of the map
                        elif (direction == "w") and (position in bad_wests):
                            event = " attempted to escape the dungeon"
                            data = {"data": gmap.map, "player": id_, "event": event}
                            return socketio.emit('my response', data)
                        # if the direction is east and they are on the right of the map
                        elif (direction == "e") and (position in bad_easts):
                            event = " attempted to escape the dungeon"
                            data = {"data": gmap.map, "player": id_, "event": event}
                            return socketio.emit('my response', data)
                        else:
                            gmap.map[position] = 0
                            gmap.map[new_position] = id_
                            current_room = gmap.rooms[new_position]
                            event = f" moved to {current_room.name}"
                            data = {"data": gmap.map, "player": id_, "event":event}
                            return socketio.emit('my response', data)
                # Runs if new position puts player off map
                else:
                    event = " attempted to escape the dungeon"
                    data = {"data": gmap.map, "player": id_, "event": event}
                    return socketio.emit('my response', data)
            # If the input direction isn't valid
            else:
                event = " attempted to escape the dungeon"
                data = {"data": gmap.map, "player": id_, "event": event}
                return socketio.emit('my response', data)
                
    
if __name__ == '__main__':
    # eventlet.monkey_patch(socket=True, select=True)
    socketio.run(app, debug=True)