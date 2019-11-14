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
STATISTICS_FILENAME = credentials_example.STATISTICS_FILENAME

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
        logger.info("POST messaged recieved on port with the following details")
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
                api.messages.create(TRACKING_ROOM_ID, text=str(room.id + " - " +
                                                               webhook_obj.data.personEmail + " - " +
                                                               message.text))
                return 'OK'
            else:
                lookup_skus = re.split(' |\n', str(message.text).upper())
                # lookup_skus = str(message.text).split("\n").split(" ")
                for sku in lookup_skus:
                    normalised_sku = sku.upper().strip(" ").strip("\n")
                    if normalised_sku == "EOL" or \
                            normalised_sku == "EOS" or \
                            normalised_sku == "CISCOEOL" or \
                            normalised_sku == "SKU" or \
                            normalised_sku == "":
                        continue
                    search_result, found_sku = search_json_for_sku(sku)
                    api.messages.create(room.id, text=search_result)
                    if found_sku:
                        results_logger.info(str(webhook_obj.data.personEmail) + " ##### " + sku)

                # Post a message to the tracking/debug room
                global SKU_LOOKUP_COUNTER
                api.messages.create(TRACKING_ROOM_ID, text=str(room.id + " - " +
                                                               webhook_obj.data.personEmail + " - " +
                                                               message.text + " - " +
                                                               str(SKU_LOOKUP_COUNTER.value)))
            return 'OK'


def load_json_from_file():
    now = datetime.now()
    datestring = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
    # local_filename = ABSOLUTE_PATH + datestring + "-Cisco_KnownGoodValues.json"
    local_filename = ABSOLUTE_PATH + "CONSTANT-Cisco_KnownGoodValues.json"
    kgv_jdata = Database(local_filename)
    return kgv_jdata


def search_json_for_sku(sku):
    found_sku = False
    try:
        return_string = ""
        return_string += "here is the EoS/EoL data for SKU: " + sku + "\n"
        return_string += "end of sale date: " + kgv_jdata[sku]["eos_date"] + "\n"
        return_string += "last date of support: " + kgv_jdata[sku]["ldos_date"] + "\n"
        return_string += "last ship date: " + kgv_jdata[sku]["last_ship_date"] + "\n"
        return_string += "migration product: " + kgv_jdata[sku]["migration"] + "\n"
        return_string += "end migration product: " + kgv_jdata[sku]["end_migration"] + "\n"
        return_string += "full URL for notice is: " + kgv_jdata[sku]["url"] + "\n"
        global SKU_LOOKUP_COUNTER
        with SKU_LOOKUP_COUNTER.get_lock():
            SKU_LOOKUP_COUNTER.value += 1
        found_sku = True
    except TypeError as e:
        if str(e) == "'NoneType' object is not subscriptable":
            return_string = sku
            return_string += " is not found in the EoS EoL database"
            return_string += " SKU is either invalid, part of a bigger SKU or not EoL.....yet"
        else:
            return_string = "something went wrong hit error "
            return_string += str(e)
    except Exception as e:
        return_string = "something went wrong hit error "
        return_string += str(e)
    return return_string, found_sku


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


def graceful_killer(signal_number, frame):
    logger.info("Got Kill signal")
    logger.info('Received:', signal_number)
    logger.info("writing some things to files")
    try:
        statistics_file = open(STATISTICS_FILENAME, 'wt')
        statistics_file.seek(0)
        statistics_file.writelines("EOL-COUNT=" + str(SKU_LOOKUP_COUNTER.value))
        statistics_file.truncate()
        statistics_file.flush()
        statistics_file.close()
        logger.info("file write complete")
    except Exception as e:
        logger.error("something went bad writing statistics file")
        logger.error("Unexpected error:", sys.exc_info()[0])
        logger.error("Unexpected error:", str(e))
    logger.info("clean close complete")
    quit()


def load_statistics_file():
    try:
        logger.info("opening statistics file")
        global SKU_LOOKUP_COUNTER
        statistics_file = open(STATISTICS_FILENAME, 'rt')
        for line in statistics_file.readlines():
            logger.info(line)
            if "EOL-COUNT" in line:
                logger.info("in loop")
                count_to_add = int(line.split("=")[-1])
                logger.info("loaded previous hit count of = " + str(count_to_add))
                with SKU_LOOKUP_COUNTER.get_lock():
                    SKU_LOOKUP_COUNTER.value += count_to_add
                logger.info("added previous hit count to current count for persistence")
        logger.info("closing statistics file")
        statistics_file.close()
        return
    except Exception as e:
        logger.error("something went bad opening statistics file")
        logger.error("Unexpected error:", sys.exc_info()[0])
        logger.error("Unexpected error:", str(e))
    return


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

    # Catch SIGTERM etc
    signal.signal(signal.SIGHUP, graceful_killer)
    signal.signal(signal.SIGINT, graceful_killer)
    signal.signal(signal.SIGQUIT, graceful_killer)
    signal.signal(signal.SIGILL, graceful_killer)
    signal.signal(signal.SIGTRAP, graceful_killer)
    signal.signal(signal.SIGABRT, graceful_killer)
    signal.signal(signal.SIGBUS, graceful_killer)
    signal.signal(signal.SIGFPE, graceful_killer)
    #signal.signal(signal.SIGKILL, graceful_killer)
    signal.signal(signal.SIGUSR1, graceful_killer)
    signal.signal(signal.SIGSEGV, graceful_killer)
    signal.signal(signal.SIGUSR2, graceful_killer)
    signal.signal(signal.SIGPIPE, graceful_killer)
    signal.signal(signal.SIGALRM, graceful_killer)
    signal.signal(signal.SIGTERM, graceful_killer)

    # Create Results logger
    results_logger = logging.getLogger("Cisco EoL EoS Request Logger")
    results_handler = logging.handlers.TimedRotatingFileHandler(RESULTSFILE, backupCount=365, when='D')
    results_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    results_handler.setFormatter(results_formatter)
    results_logger.addHandler(results_handler)
    results_logger.setLevel(logging.INFO)

    logger.info("Load stats")
    load_statistics_file()
    logger.info("Load EoL data ")
    kgv_jdata = load_json_from_file()
    logger.info("deleting old webhook")
    delete_webhook(api=api)
    logger.info("creating new webhook")
    create_webhook(api=api)
    http_server = wsgiserver.WSGIServer(host=FLASK_HOST, port=FLASK_PORT, wsgi_app=flask_app)
    http_server.start()