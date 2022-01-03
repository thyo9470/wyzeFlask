import os
import wyze_sdk
from room_bulbs import room_bulbs
from wyze_sdk.errors import WyzeApiError
from flask import Flask, request

client = wyze_sdk.Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])

app = Flask(__name__)

@app.route('/')
def ping():
    return 'I am alive!'

def create_toggle_response(status_code, message):
  response = dict()
  response['status_code'] = status_code
  response['message'] = message
  return response

@app.route('/toggle_light')
def toggle_light():

  target_room = request.args.get('room')

  # Check if room is given
  if target_room == None:
    return create_toggle_response(400, 'missing target room')

  # Check if room exists
  if target_room not in room_bulbs.keys():
    return create_toggle_response(400, f"room given is not a supported room. Supported rooms: {room_bulbs.keys()}")

  # get first bulb info
  first_bulb = client.bulbs.info(device_mac=room_bulbs[target_room][0])

  for bulb_mac in room_bulbs[target_room]:
    try:
      bulb = client.bulbs.info(device_mac=bulb_mac)

      # check if bulb online
      if not bulb.is_online:
        continue

      if first_bulb.is_on:
        client.bulbs.turn_off(device_mac=bulb.mac, device_model=bulb.product.model)
      else:
        client.bulbs.turn_on(device_mac=bulb.mac, device_model=bulb.product.model)

    except WyzeApiError as e:
        # You will get a WyzeApiError if the request failed
        print(f"Got an error: {e}")
        return create_toggle_response(500, 'an error occurred when contacting wyze')

  return create_toggle_response(200, 'success')
  
