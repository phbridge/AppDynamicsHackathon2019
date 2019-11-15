#Snapshot Code

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
    meraki_snapshot_url_creation_time = meraki_snapshot_finish_time - meraki_snapshot_start_time    ########################

    print('another mugshot done')

    camerasnaps =[]
    camerasnaps.append(CA2_response.json()["url"])


    return camerasnaps, meraki_snapshot_url_creation_time

