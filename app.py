from flask import Flask, render_template
from flask_socketio import SocketIO
import random
from pyscripts.game_classes import *
from pyscripts.database_class import *


gmap = gameMap()
num_players = 0
players = []

connector = dbConnector()

# Create flask app
app = Flask(__name__)
# Set app's secret key
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
# Wrap Socketio around app
socketio = SocketIO(app)

# Start Screen
@app.route('/')
def start():
    return render_template('start.html')

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
        # Set a random spawn location
        position = random.randint(0, 100)
        # create player object with position and id
        player = Player(position, id_) 
        # append new player to players
        players.append(player)
        # Update gamemap to include player
        gmap.map[player.location] = player.id_
        # Increment amount of players by 1
        num_players += 1
        message = f"Player {id_} has joined the dungeon"
        # Create the data that will be sent back(map cords and players id)
        data = {"data": gmap.map, "player": player.id_, "message": message}
        # sent client data
        return socketio.emit('my response', data)
    # Runs if user sent a message
    if data["message"] != '':
        data = {"data": gmap.map, "player": data["player"], "message": data["message"]}
        socketio.emit('my response', data)
    # Runs if client is already connected
    else:
        # Grab the players id from data recieved
        id_ = int(data["player"])
        # Check direction inputed
        direction = data["data"]
        # Check players current position on map
        position = gmap.map.index(id_)
        # runs if input direction is invalid
        if direction.lower() not in ["forward", "backward", "f", "b"]:
            data = {"data": gmap.map, "player": id_}
            socketio.emit('my response', data)
        # Runs if input position is valid and they are in the first room
        if position == 0:
            # if they are moving forward
            if direction.lower() in ["forward", "f"]:
                # Change map accordingly
                gmap.map[position] = 0
                gmap.map[position+1] = id_
            # Create data and send to client
            data = {"data": gmap.map, "player": id_}
            socketio.emit('my response', data)
        # Runs if player isn't in the first or last room
        elif (position > 0) and (position <= 98):
            # Runs if they are moving forward
            if direction.lower() in ["forward", "f"]:
                gmap.map[position] = 0
                gmap.map[position+1] = id_
            # Runs if they are moving backward
            if direction.lower() in ["backward", "b"]:
                gmap.map[position] = 0
                gmap.map[position-1] = id_
            data = {"data": gmap.map, "player": id_}
            socketio.emit('my response', data)
        # Runs if player is in last room
        else:
            # Runs if they want to go backwards
            if direction.lower() in ["backward", "b"]:
                gmap.map[position] = 0
                gmap.map[position+1] = id_
            data = {"data": gmap.map, "player": id_}
            socketio.emit('my response', data)
    


if __name__ == '__main__':
    socketio.run(app, debug=True)