#Snapshot Code for Who the Fuck are you!

import requests
import json

import requests
import credentials_example

CameraOne = "https://api.meraki.com/api/v0/networks/L_706502191543747121/cameras/Q2FV-363D-9Z7Z/snapshot"
CameraTwo = "https://api.meraki.com/api/v0/networks/L_706502191543747121/cameras/Q2FV-PN2M-VA5E/snapshot"

def snapshot():
    headers = {
        'X-Cisco-Meraki-API-Key': credentials_example.MERAKI_API,
        'Content-Type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
        }

    CA1_response = requests.request("POST", CameraOne, headers=headers)
    CA2_response = requests.request("POST", CameraTwo, headers=headers)

    camerasnaps =[]

    camerasnaps.append(CA1_response.json()["url"])
    camerasnaps.append(CA2_response.json()["url"])
#print(CA1_response.url)
#print(CA2_response.url)

    return camerasnaps