#Snapshot Code for Who the Fuck are you!

import requests
import json

import requests
import credentials
import time

CameraOne = "https://api.meraki.com/api/v0/networks/{}/cameras/{}/snapshot".format(credentials.MERAKINETID, credentials.CAMERA_1)
CameraTwo = "https://api.meraki.com/api/v0/networks/{}/cameras/{}/snapshot".format(credentials.MERAKINETID, credentials.CAMERA_2)

def snapshot():
    headers = {
        'X-Cisco-Meraki-API-Key': credentials.MERAKI_API,
        'Content-Type': "application/x-www-form-urlencoded",
        }
    CA2_response = requests.request("POST", CameraTwo, headers=headers)
    CA1_response = requests.request("POST", CameraOne, headers=headers)

    #The proper list to return
    camerasnaps =[]

    camerasnaps.append(CA1_response.json()["url"])
    camerasnaps.append(CA2_response.json()["url"])

    #Give two snapshots of the same image to Phil
    cameraphil =[]
    cameraphil.append(CA1_response.json()["url"])
    cameraphil.append(CA1_response.json()["url"])

    return camerasnaps

    #return camerasnaps