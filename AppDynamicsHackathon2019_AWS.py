# Copyright (c) 2021 Cisco and/or its affiliates.
#
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.1 (the "License"). You may obtain a copy of the
# License at
#
#                https://developer.cisco.com/docs/licenses
#
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

# Title
# AWS BoTo for Recognition
#
# Language
# Python 3.5
#
# Description
# This script will do face comparison/recognition for two image URL's and return a confidence score as a string
#
# Contacts
# Phil Bridges - phbridge@cisco.com
#
# EULA
# This software is provided as is and with zero support level. Support can be purchased by providing Phil bridges with a
# varity of Beer, Wine, Steak and Greggs pasties. Please contact phbridge@cisco.com for support costs and arrangements.
# Until provison of alcohol or baked goodies your on your own but there is no rocket sciecne involved so dont panic too
# much. To accept this EULA you must include the correct flag when running the script. If this script goes crazy wrong and
# breaks everything then your also on your own and Phil will not accept any liability of any type or kind. As this script
# belongs to Phil and NOT Cisco then Cisco cannot be held responsable for its use or if it goes bad, nor can Cisco make
# any profit from this script. Phil can profit from this script but will not assume any liability. Other than the boaring
# stuff please enjoy and plagerise as you like (as I have no ways to stop you) but common curtacy says to credit me in some
# way [see above comments on Beer, Wine, Steak and Greggs.].
#
#
# Version Control               Comments
# Version 0.01 Date 14/11/19    Inital draft
#
# Version 6.9 Date xx/xx/xx     Took over world and actuially got paid for value added work....If your reading this
#                               approach me on linkedin for details of weekend "daily" rate
# Version 7.0 Date xx/xx/xx     Note to the Gaffer - if your reading this then the above line is a joke only :-)
#
# ToDo *******************TO DO*********************
# 1.0 Import AWS module             DONE
# 2.0 Import credentials            DONE
# 3.0 Initiate client               DONE
# 4.0 Use client for images         DONE
# 5.0 Return data in nice format    DONE
# 6.0 Tidy up messy crap
#
#

import boto3
import requests
from io import BytesIO
import credentials
import time
from datetime import datetime

aws_access_key_id = credentials.aws_access_key_id
aws_secret_access_key = credentials.aws_secret_access_key
aws_region = credentials.aws_region

#SRC_FILE_URL = "https://spn3.meraki.com/stream/jpeg/snapshot/753a73e5eaa3c047VHZjJjY2IzMmQ3YWYyZGM4YjZkMjhhNzA1OWIwZDExZDRmYWU3YmYwMWM2MGRmNGIyZjBkMzI2MmJmMTY3NzI2N2XrKemmY6sAk5mMUvxYtuvL5SxNuHGFNtVO3zHBse0SXhVR9MvyZW-yY94Bj5mp_3vfkPZmQSIitBxM1hxg7wD8PjkbkzeQ1Plc1gtb1j55aWjPiR7DfOvI2FJSKFAIhh2A9SZ4JIT1XedQCiIlKEMY1hh5Ts7Y2EajZ5VKSqTDOIuRlZosiECoEwXmjMHaV93JZiNgcydMnyEQbsVVpUE"
#DST_FILE_URL = "https://spn3.meraki.com/stream/jpeg/snapshot/753a73e5eaa3c047VHY2Q3ZmU2MmI3NjUyNDUzZjM3NjExZWI0NDRhOTYwNjk3MzFjNGFlMmU2Y2Q0ZDVjNTc4MjYxZjVmNDA1MjY3Ocf3_bDTWXasvH29tW-OFY6VZp-p3yQLFwdjg0hJYzTTbokvFmalupxQ9ccJAzxL0Wq8q3Qf_kOb5m5t1NtTTj8LCrtBBm2f5v1TYe-4iz6q592mbWNpaL9_2JCpyYXSLa2OPvADaWrpnALjDsBqyc7dCtmoUWC531JPlVft18NSHJJKeMRfXReEzQE-9-PFXcBVP6uuAQ265w967QosaOo"


def _get_images_from_local(src_path, dst_path):
    imageSource = open(src_path, 'rb')
    imageTarget = open(dst_path, 'rb')
    return _compare_faces(imageSource, imageTarget)


def get_images_from_LOCAL_and_URL(srcimage, dst_url):
    print(dst_url)
    time.sleep(5)
    start_time_meraki_get = datetime.now()      #########
    dstresponse = requests.get(dst_url)
    finish_time_meraki_get = datetime.now()     #########
    meraki_fetch_time = finish_time_meraki_get - start_time_meraki_get      #####################
    if dstresponse.status_code == 200:
        imageTarget = BytesIO(dstresponse.content)
    else:
        return "Image target not valid URL status code " + str(dstresponse.status_code)
    return _compare_faces(srcimage, imageTarget)


def get_images_from_URL(src_url, dst_url):
    time.sleep(2)
    srcresponse = requests.get(src_url)
    if srcresponse.status_code == 200:
        imageSource = BytesIO(srcresponse.content)
    else:
        return "Image source not valid URL status code " + str(srcresponse.status_code)
    time.sleep(2)
    dstresponse = requests.get(dst_url)
    if dstresponse.status_code == 200:
        imageTarget = BytesIO(dstresponse.content)
    else:
        return "Image target not valid URL status code " + str(dstresponse.status_code)
    return _compare_faces(imageSource, imageTarget)


def _compare_faces(imageSource, imageTarget):
    responder = ""
    client = boto3.client('rekognition', region_name=aws_region,
                          aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key)
    imageTarget.seek(0)
    try:
        start_time_aws_get = datetime.now()                         #########
        response = client.compare_faces(SimilarityThreshold=30, SourceImage={'Bytes': imageSource.read()}, TargetImage={'Bytes': imageTarget.read()})
        finish_time_aws_get = datetime.now()                        #########
        aws_fetch_time = finish_time_aws_get - start_time_aws_get  #####################
        print(str(response))
    except client.exceptions.InvalidParameterException as e:
        responder = "no face detected in one of the images"
        return responder
    except Exception as e:
        responder = "something went wrong hit error "
        responder += str(e)
        return responder

    similarity = "0"
    for faceMatch in response['FaceMatches']:
        position = faceMatch['Face']['BoundingBox']
        similarity = str(faceMatch['Similarity'])
        print('The face at ' +
              str(position['Left']) + ' ' +
              str(position['Top']) +
              ' matches with ' + similarity + '% confidence')

    imageSource.close()
    imageTarget.close()

    print(str(len(response['FaceMatches'])))
    if int(len(response['FaceMatches'])) == 1:
        responder = "The person is genuine we are " + str(similarity)[0:5] + " confident about this"
    else:
        responder += "WARNING WARNING\n"
        responder += "The person is NOT genuine INTERROGATE THEM \n"
        responder += "WARNING WARNING\n"
    return responder


def main():
    print("null")

    src_url = "https://spn3.meraki.com/stream/jpeg/snapshot/753a73e5eaa3c047VHYWYzYTZhNTNlYWI4MDk1ZDcyYTkwN2M4YzBmNDllODNmZDFhMGUzMTE4M2UwMmQ4NmE1ZDc0NmNkZTdiZjhkY9ceNa7vgM2O90Oorr3FVVNnVwXbUEESzpciOkFEHVC4sji0hj0vL44In6tW_b2GExANNnHv9v_30m3wY_sqMEOJtbkqM7Ix1Bnvsl_hD1Evms8hcozFsjtuNC89B8-qzMq-tcZEYEZJq6D-UhQ1d2wzj8vW6LuhtteT3Ui92Ig_yNwMtaIUXg0RDica3y5r7XAy6ajT3Yzc9ZmMiB1poBo"
    dst_url = "https://spn3.meraki.com/stream/jpeg/snapshot/753a73e5eaa3c047VHZmI5YjdiYmYyYzc0YTZlZTAxYjU3YTU2MzRjZDAxNGUzYzRkZjU3MmYyNDEyNTgyYTQ1MjZiZTI2NGM2YWE4Nb7JlF8myl-orv7f1YNQ9GIHm48f9fETQ_NMjGjDRpmcYK6K4KqFp5KXq38oaSsvF8jWx9Vj17Rypx8Pk9Gl_fUTA92_6JvqLLMKJk8bYXf9Kla_nFrKWwWg6fCTjQMmsPvvWLPn3p5lIRS9FMbYgx1galY7hCbEnSIQyd9gf2xqmltjA6vG-6sDzN2HUvd9PhgAsNGAdpOUrxJ5TyiHUlk"

    print(get_images_from_URL(src_url, dst_url))
    #face_matches = _get_images_from_local(SRC_FILE, DST_FILE)
    #URL_face_matches = get_images_from_URL(SRC_FILE_URL, DST_FILE_URL)
    #print("Face matches: " + str(face_matches))
    #print("Face matches: " + str(URL_face_matches))


if __name__ == "__main__":
    main()
