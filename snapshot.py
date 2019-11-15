#Snapshot Code for Who the Fuck are you!

import requests
import json
import time
import requests
import credentials
import time
from datetime import datetime

CameraOne = "https://api.meraki.com/api/v0/networks/{}/cameras/{}/snapshot".format(credentials.MERAKINETID, credentials.CAMERA_1)
CameraTwo = "https://api.meraki.com/api/v0/networks/{}/cameras/{}/snapshot".format(credentials.MERAKINETID, credentials.CAMERA_2)

def snapshot():
    headers = {
        'X-Cisco-Meraki-API-Key': credentials.MERAKI_API,
        'Content-Type': "application/x-www-form-urlencoded",
        }
    print('photo taken')
    meraki_snapshot_start_time = datetime.now()                     ############
    CA2_response = requests.request("POST", CameraOne, headers=headers)
    meraki_snapshot_finish_time = datetime.now()  ############
    maraki_snapshot_url_creation_time = meraki_snapshot_finish_time - meraki_snapshot_start_time    ########################
    # time.sleep(15)
    #
    # CA1_response = requests.request("POST", CameraOne, headers=headers)
    print('another mugshot done')

    #The proper list to return
    camerasnaps =[]

    # camerasnaps.append(CA1_response.json()["url"])
    camerasnaps.append(CA2_response.json()["url"])

    #Give two snapshots of the same image to Phil
    # cameraphil =[]
    # cameraphil.append(CA1_response.json()["url"])
    # cameraphil.append(CA1_response.json()["url"])

    return camerasnaps

    #return camerasnaps