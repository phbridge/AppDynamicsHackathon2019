# Title
# Get_Check_EOL
#
# Language
# Python 3.5
#
# Description
# This script will return the EoS/EoL notice when you give it a valid SKU from a known list of published EoS/EoL
# notices. This script will only return public notices on Cisco.com. The sourcing for this is part of a seperate script.
# This only covers the Bot responding and pulling the data from JSON. Not the scrape of the origional Data.
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
# Version 0.01 Date 16/07/19    Inital draft
#
# Version 6.9 Date xx/xx/xx     Took over world and actuially got paid for value added work....If your reading this
#                               approach me on linkedin for details of weekend "daily" rate
# Version 7.0 Date xx/xx/xx     Note to the Gaffer - if your reading this then the above line is a joke only :-)
#
# ToDo *******************TO DO*********************
# 1.0 Import data from JSON     DONE
# 2.0 Respond to WebHook        DONE
# 3.0 Colect messages           DONE
# 4.0 Parse messages            DONE
# 5.0 respond to messages       DONE
# 6.0 statistics
# 7.0 wildecard search/match
# 8.0 SKU validation
#

from webexteamssdk import WebexTeamsAPI, Webhook    # builds WebHook and posts messages
from flask import request, Flask                    # Flask website
from datetime import datetime                       # timestamps mostly
import credentials_example                          # imports static values
import logging.handlers                             # Needed for logging
import re                                           # Matching SKU's
import wsgiserver                                   # Runs the Flask webesite
from multiprocessing import Value                   # keeps counts of things
import signal                                       # catches SIGTERM and SIGINT
import sys                                          # for error to catch and debug
import snapshot

FLASK_HOST = credentials_example.FLASK_HOST
FLASK_PORT = credentials_example.FLASK_PORT
FLASK_HOSTNAME = credentials_example.FLASK_HOSTNAME
TARGET_URL = "http://" + FLASK_HOSTNAME + ":" + str(FLASK_PORT) + "/"
BOT_ACCESS_TOKEN = "Bearer " + credentials_example.BOT_ACCESS_TOKEN
ABSOLUTE_PATH = credentials_example.ABSOLUTE_PATH
LOGFILE = credentials_example.LOGFILE
LOGFILE_MAX_SIZE = credentials_example.LOGBYTES
LOGFILE_COUNT = credentials_example.LOGCOUNT
RESULTSFILE = credentials_example.RESULTSFILE
TRACKING_ROOM_ID = credentials_example.TRACKING_ROOM_ID


api = WebexTeamsAPI(access_token=credentials_example.BOT_ACCESS_TOKEN)

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
            if "HELP" in str(message.text).upper() or "?" in message.text:
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
                        api.messages.create(room.id, text=newmessage)

                        continue
                    # normalised_sku = "you typed" + go
                    #search_result, found_sku = search_json_for_sku(sku)
                    # api.messages.create(room.id, text=newmessage)
                        # if found_sku:
                        #     results_logger.info(str(webhook_obj.data.personEmail) + " ##### " + sku)

                # Post a message to the tracking/debug room
                # global SKU_LOOKUP_COUNTER
                # api.messages.create(TRACKING_ROOM_ID, text=str(room.id + " - " +
                #                                                webhook_obj.data.personEmail + " - " +
                #                                                message.text + " - " +
                #                                                str(SKU_LOOKUP_COUNTER.value)))
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