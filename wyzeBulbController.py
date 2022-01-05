import os
import wyze_sdk
from wyze_sdk.errors import WyzeApiError, WyzeRequestError
from multiprocessing import Process, Manager

class WyzeBulbController():

  def __init__(self):
    self.client = wyze_sdk.Client(email=os.environ['WYZE_EMAIL'], password=os.environ['WYZE_PASSWORD'])

  '''
    Toggles the given light to be on or off using wyze sdk.
    You can give a light's on status to ensure a series of lights are in sync,
    otherwise the given bulbs is_on status will be used

    param mac_addr - (string) the mac address of the target bulb
    param is_on    - (bool) (optional) the current bulb state, defaults to the bulb state of retrieved with the given max address 
    param exception_arr - (exception[]) (optional) if set, any exceptions that occurred are appended to the array'''
  def toggle_light(self, mac_addr, is_on=None, exception_arr=[]):
    try:
      bulb = self.client.bulbs.info(device_mac=mac_addr)

      if not bulb.is_online:
        print(f"The {bulb.nickname} ({bulb.mac}) bulb is offline")
        raise Exception(f"The {bulb.nickname} ({bulb.mac}) bulb is offline")

      if is_on == None:
        is_on = bulb.is_on

      if is_on:
        self.client.bulbs.turn_off(device_mac=bulb.mac, device_model=bulb.product.model)
      else:
        self.client.bulbs.turn_on(device_mac=bulb.mac, device_model=bulb.product.model)
    except WyzeApiError as e:
      print(f"Got an error when toggling {bulb.nickname} ({bulb.mac}): {e}")
      exception_arr.append(e)
    except Exception as e:
      print(f"Got an error: {e}")
      exception_arr.append(e)
        

  '''
    Calls the toggle bulb function on a set of bulbs in parralel. Toggle is based on the first bulbs on state.

    param mac_addrs - (string[]) list of max address for the target bulbs to toggle
  '''
  def toggle_in_parrallel(self, mac_addrs):
    with Manager() as manager:
      first_bulb = self.client.bulbs.info(device_mac=mac_addrs[0])
      exception_arr = manager.list()
      proc = []
      for addr in mac_addrs:
        p = Process(target=self.toggle_light, args=(addr,first_bulb.is_on,exception_arr))
        p.start()
        proc.append(p)
      for p in proc:
        p.join()
      if len(exception_arr) > 0:
        print("test")
        raise Exception("There was an error toggling the lights: \n{}".format('\n'.join([str(e) for e in exception_arr])))
