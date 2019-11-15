# Title
# Snapshot BOT
#
# Language
# Python 3.7
#
# Description
# This BOT will take two snapshots from two Meraki MV Sense cameras.  The snapshots will be sent to AWS for comparison.
# Result of the comparison will be sent back to the Webex Teams room from which the Bot request was 
# initiated from.
#
# Contacts
# Phil Bridges - phbridge@cisco.com
# Simon Hart - sihart@cisco.com
# Eirini Spanou - espanou@cisco.com
#
# EULA
# This software is provided as is and with zero support level. Support can be purchased by providing any of the above contacts
#  with a variety of Beer, Wine, Steak and Greggs pasties. Please contact phbridge@cisco.com for support costs and arrangements.
# Until provision of alcohol or baked goodies your on your own but there is no rocket sciecne involved so dont panic too
# much. To accept this EULA you must include the correct flag when running the script. If this script goes crazy wrong and
# breaks everything then your also on your own and we will not accept any liability of any type or kind. As this script
# belongs to us and NOT Cisco then Cisco cannot be held responsible for its use or if it goes bad, nor can Cisco make
# any profit from this script. We can profit from this script but will not assume any liability. Other than the boring
# stuff please enjoy and plagiarise as you like (as I have no ways to stop you) but common courtesy says to credit us in some
# way [see above comments on Beer, Wine, Steak and Greggs.].
#
#
# Version Control               Comments
# Version 0.01 Date 14/11/19   Initial draft
#
# Version 6.9 Date xx/xx/xx     Took over world and actuially got paid for value added work....If your reading this
#                               approach me on linkedin for details of weekend "daily" rate
# Version 7.0 Date xx/xx/xx     Note to the Gaffer - if your reading this then the above line is a joke only :-)
#
# ToDo *******************TO DO*********************


from webexteamssdk import WebexTeamsAPI, Webhook    # builds WebHook and posts messages
from flask import request, Flask                    # Flask website
from datetime import datetime                       # timestamps mostly
import credentials                          # imports static values
import logging.handlers                             # Needed for logging
import re                                           # Matching SKU's
import wsgiserver                                   # Runs the Flask webesite
from multiprocessing import Value                   # keeps counts of things
import signal                                       # catches SIGTERM and SIGINT
import sys                                          # for error to catch and debug
import snapshot
import AppDynamicsHackathon2019_AWS
import requests
from io import BytesIO

FLASK_HOST = credentials.FLASK_HOST
FLASK_PORT = credentials.FLASK_PORT
FLASK_HOSTNAME = credentials.FLASK_HOSTNAME
TARGET_URL = "http://" + FLASK_HOSTNAME + ":" + str(FLASK_PORT) + "/"
BOT_ACCESS_TOKEN = "Bearer " + credentials.BOT_ACCESS_TOKEN
ABSOLUTE_PATH = credentials.ABSOLUTE_PATH
LOGFILE = credentials.LOGFILE
LOGFILE_MAX_SIZE = credentials.LOGBYTES
LOGFILE_COUNT = credentials.LOGCOUNT
RESULTSFILE = credentials.RESULTSFILE
TRACKING_ROOM_ID = credentials.TRACKING_ROOM_ID


api = WebexTeamsAPI(access_token=credentials.BOT_ACCESS_TOKEN)

flask_app = Flask(__name__)

SKU_LOOKUP_COUNTER = Value('i', 0)


@flask_app.route('/', methods=['GET', 'POST'])
def webex_teams_webhook_events():
    """Processes incoming requests to the '/events' URI."""
    if request.method == 'GET':
        logger.info("GET request recieved on port responding")
        return ("""<!DOCTYPE html>
                   <html lang="en">
                       <head>
                           <meta charset="UTF-8">
                           <title>WORKING</title>
                       </head>
                   <body>
                   <p>
                   <strong>WORKING</strong>
                   </p>
                   </body>
                   </html>
                """)
    elif request.method == 'POST':
        logger.info("POST messaged received on port with the following details")
        json_data = request.json
        logger.info(str(json_data))
        # Create a Webhook object from the JSON data
        webhook_obj = Webhook(json_data)
        # Get the room details
        room = api.rooms.get(webhook_obj.data.roomId)
        # Get the message details
        message = api.messages.get(webhook_obj.data.id)
        # Get the sender's details
        person = api.people.get(message.personId)

        logger.debug("NEW MESSAGE IN ROOM '{}'".format(room.title))
        logger.debug("FROM '{}'".format(person.displayName))
        logger.debug("MESSAGE '{}'\n".format(message.text))

        # This is a VERY IMPORTANT loop prevention control step.
        me = api.people.me()
        if message.personId == me.id:
            # Message was sent by me (bot); do not respond.
            logger.info("checked message but it was from me")
            return 'OK'

        else:
            # Message was sent by someone else; parse message and respond.
            if message.files:
                print(message.files)

                headers= {
    'Authorization': "Bearer ZTlhN2Y3YWYtOWYwNC00YWIzLTk0YjktMWY1Y2UxMjI4ODY0ZTNhN2FiN2QtMWRi_PF84_1eb65fdf-9643-417f-9974-ad72cae0e10f",
    'cache-control': "no-cache",
    'Postman-Token': "7c9aaad4-88a7-4206-9a7d-28fd442dc59d"
    }

                dstresponse = requests.get(message.files[0], headers=headers)
                print("################GOT DST")
                if dstresponse.status_code == 200:
                    imageTarget = BytesIO(dstresponse.content)
                print("################GOT DST Content")
                print(type(imageTarget))

                camsnapshots = snapshot.snapshot()
                newmessage = camsnapshots[0]
                print(camsnapshots[0])
                recognition = AppDynamicsHackathon2019_AWS.get_images_from_LOCAL_and_URL(imageTarget,camsnapshots[0])
                api.messages.create(room.id, text=str(recognition))





            elif "HELP" in str(message.text).upper() or "?" in message.text:
                return_messsage = """Welcome to the Cisco AppD Who the F**k are you bot!!!!


                The Bot will respond to the following commands:
                'help'          - displays this text
                '?'             - displays this text
                'Go'            - Will initiate a snapshot of Imposter and Identity
                """

                # Post the fact to the room where the request was received
                api.messages.create(room.id, text=return_messsage)
                # Post a message to the tracking/debug room
                # api.messages.create(TRACKING_ROOM_ID, text=str(room.id + " - " +
                #                                                webhook_obj.data.personEmail + " - " +
                #                                                message.text))
                return 'OK'

            # if message.files:
            #     print(message.files)

            else:
                lookup_go = re.split(' |\n', str(message.text).upper())
                # lookup_go = str(message.text).split("\n").split(" ")
                for go in lookup_go:
                    normalised_sku = go.upper().strip(" ").strip("\n")
                    if normalised_sku == "GO" or \
                            normalised_sku == "go" :

                        camsnapshots = snapshot.snapshot()
                        newmessage=camsnapshots[0]
                        print(camsnapshots[0])
                        recognition = AppDynamicsHackathon2019_AWS.get_images_from_URL(camsnapshots[0], camsnapshots[1])
                        api.messages.create(room.id, text=str(recognition))

                        #recognition = AppDynamicsHackathon2019_AWS.get_images_from_URL(camsnapshots[0],camsnapshots[0])

                        continue

            return 'OK'







def delete_webhook(api):
    """Find a webhook by name."""
    for webhook in api.webhooks.list():
        if webhook.name == "CiscoEoLBot":
            print("Deleting Webhook:", webhook.name, webhook.targetUrl)
            logger.info("Deleting Webhook:" + webhook.name + webhook.targetUrl)
            api.webhooks.delete(webhook.id)


def create_webhook(api):
    """Create a Webex Teams webhook pointing to the public URL."""
    print("Creating Webhook...")
    webhook = api.webhooks.create(
        name="CiscoEoLBot", targetUrl=TARGET_URL, resource="messages", event="created", )
    print(webhook)
    print("Webhook successfully created.")
    logger.info("Webhook successfully created.")
    return webhook





if __name__ == "__main__":
    # Create Logger
    logger = logging.getLogger("Cisco EoL EoS Logger")
    handler = logging.handlers.RotatingFileHandler(LOGFILE, maxBytes=LOGFILE_MAX_SIZE, backupCount=LOGFILE_COUNT)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info("---------------------- STARTING ----------------------")
    logger.info("cisco EoS EoL script started")


    # Create Results logger
    results_logger = logging.getLogger("Cisco EoL EoS Request Logger")
    results_handler = logging.handlers.TimedRotatingFileHandler(RESULTSFILE, backupCount=365, when='D')
    results_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    results_handler.setFormatter(results_formatter)
    results_logger.addHandler(results_handler)
    results_logger.setLevel(logging.INFO)

    logger.info("Load stats")
    logger.info("Load EoL data ")
    logger.info("deleting old webhook")
    delete_webhook(api=api)
    logger.info("creating new webhook")
    create_webhook(api=api)
    http_server = wsgiserver.WSGIServer(host=FLASK_HOST, port=FLASK_PORT, wsgi_app=flask_app)
    http_server.start()
    #message_to_send = ApPDynamicsHackaton2019_AWS(snapshot)