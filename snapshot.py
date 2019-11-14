#Snapshot Code for Who the Fuck are you!

import requests
import json

import requests
import credentials

CameraOne = "https://api.meraki.com/api/v0/networks/{}/cameras/{}/snapshot".format(credentials.MERAKINETID, credentials.CAMERA_1)
CameraTwo = "https://api.meraki.com/api/v0/networks/{}/cameras/{}/snapshot".format(credentials.MERAKINETID, credentials.CAMERA_2)

def snapshot():
    headers = {
        'X-Cisco-Meraki-API-Key': credentials.MERAKI_API,
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        }

    CA1_response = requests.request("POST", CameraOne, headers=headers)
    CA2_response = requests.request("POST", CameraTwo, headers=headers)

    camerasnaps =[]

    camerasnaps.append(CA1_response.json()["url"])
    camerasnaps.append(CA2_response.json()["url"])
    print(camerasnaps)
#print(CA1_response.url)
#print(CA2_response.url)

    return camerasnaps