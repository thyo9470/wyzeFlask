from wyzeBulbController import WyzeBulbController
from room_bulbs import room_bulbs
from flask import Flask, request, Response

app = Flask(__name__)

wyzeBulbController = WyzeBulbController()

'''
  Flask route to confirm flask is running
'''
@app.route('/')
def ping():
    return Response("I am alive!", 200)

'''
  Flask route for toggle lights in a given room.

  param room - (string) the room in which the lights should be toggles on/off
'''
@app.route('/toggle_light')
def request_toggle_light():

  target_room = request.args.get('room')

  # Check if room is given
  if target_room == None:
    return Response('missing target room', 400)

  # Check if room exists
  if target_room not in room_bulbs.keys():
    return Response(f"room given is not a supported room. Supported rooms: {room_bulbs.keys()}", 400) 

  try:
    wyzeBulbController.toggle_in_parrallel(room_bulbs[target_room])
  except Exception as e:
    print(f"Exception thrown when running toggle in parrallel: {e}")
    return Response(f"Failed trying to toggle lights: \n{e}", 500)
  

  return Response("successfully toggled {room}'s lights".format(room = target_room.replace("_", " ")), 200)
  
