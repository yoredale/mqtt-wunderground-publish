#!/usr/bin/python
"""
publish.py
Simple MQTT subscriber of weather data then publishing it to the WeatherUnderground API.
Uploads the current temperature, humidity, wind speed and wind direction from a given Personal Weather Station
"""

# IMPORTS
import urllib.request as urllib2
import urllib.parse
import json
import paho.mqtt.client as paho
import os
import logging
import sys
import datetime

# Log to STDOUT
logger = logging.getLogger("mqtt-wunderground")
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

# Component config
config = {}
config['wu_id'] = ""
config['wu_key'] = ""

sub_topics = {}
sub_topics['Humidity'] = "humidity"
sub_topics['Temperature'] = "tempc"
sub_topics['AirPressure'] = "baromhpa"
sub_topics['dewpoint'] = 'dewptf'


# Get MQTT servername/address
# Supports Docker environment variable format MQTT_URL = tcp://#.#.#.#:1883
MQTT_URL = os.environ.get('MQTT_URL')
config['broker_user'] = os.environ.get('MQTT_USR')
config['broker_password'] = os.environ.get('MQTT_PWD')
if MQTT_URL is None:
    logger.info("MQTT_URL is not set, using default localhost:1883")
    config['broker_address'] = "localhost"
    config['broker_port'] = 1883
else:
    config['broker_address'] = MQTT_URL.split("//")[1].split(":")[0]
    config['broker_port'] = 1883

# Get config topic
config['config_topic'] = os.environ.get('CONFIG_TOPIC')
if config['config_topic'] is None:
    logger.info("CONFIG_TOPIC is not set, exiting")
    raise sys.exit()

# Get Weather Underground PWS ID
config['wu_id'] = os.environ.get('CONFIG_WU_ID')
if config['wu_id'] is None:
    logger.info("CONFIG_WU_ID is not set, exiting")
    raise sys.exit()

# Get Weather Underground PWS KEY
config['wu_key'] = os.environ.get('CONFIG_WU_KEY')
if config['wu_key'] is None:
    logger.info("CONFIG_WU_KEY is not set, exiting")
    raise sys.exit()

def degc_to_degf(temp_c):
    temp_f = (temp_c * (9/5.0)) +32
    return round(temp_f,1)

def fix_pressure(pressure_in_hpa,temperature):
    msl_pressure = pressure_in_hpa / pow((1 - (1.3 / (temperature + 273.15))), 5.255)
    pressure_in_inches_of_m = msl_pressure * 0.02953
    return round(pressure_in_inches_of_m,2)

def calculate_dewpoint(temperature, humidity):
    dewpoint = temperature - ((100 - humidity) / 5)
    return dewpoint

# Create the callbacks for Mosquitto
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to broker " + str(config['broker_address'] + ":" + str(config['broker_port'])))

        # Subscribe to device config
        logger.info("Subscribing to device config at " + config['config_topic'])
        client.subscribe(config['config_topic'])


def on_subscribe(mosq, obj, mid, granted_qos):
    logger.info("Subscribed with message ID " + str(mid) + " and QOS " + str(granted_qos) + " acknowledged by broker")


def on_message(mosq, obj, msg):
    payload_as_string = msg.payload.decode("utf-8")
    logger.info("Received message: " + msg.topic + ": " + payload_as_string)
    if msg.topic == config['config_topic']:

        parsed_json = json.loads(payload_as_string)

        # Calculate dew point
        # parsed_json['dewpoint'] = parsed_json['temperature'] - ((100.0 - parsed_json['humidity']) / 2.788 )

        wu_url = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?action=updateraw" + \
                 "&ID=" + config['wu_id'] + \
                 "&PASSWORD=" + config['wu_key']

        for key in parsed_json:
            if key == "object":
                for skey in parsed_json[key]:
                    if skey == "Temperature":
                        arg_name = "tempf"
                        value = urllib.parse.quote(str(degc_to_degf(parsed_json[key][skey])))
                        wu_url += ('&' + arg_name + '=' + value)
                        logger.info('Temperature: ' + value + 'degF, ' + str(parsed_json[key][skey]) + 'degC')
                    if skey == "AirPressure":
                        arg_name = "baromin"
                        value = urllib.parse.quote(str(fix_pressure(parsed_json[key][skey], parsed_json["object"]["Temperature"])))
                        wu_url += ('&' + arg_name + '=' + value)
                        logger.info('Pressure: ' + value + 'inHg, ' + str(parsed_json[key][skey]) + 'hPa')
                    if skey == "Humidity":
                        arg_name = "humidity"
                        value = urllib.parse.quote(str(parsed_json[key][skey]))
                        wu_url += ('&' + arg_name + '=' + value)
                        logger.info('Humidity: ' + value + '%')
        arg_name = "dewptf"
        value = urllib.parse.quote(str(degc_to_degf(calculate_dewpoint(parsed_json["object"]["Temperature"],parsed_json["object"]["Humidity"]))))
        wu_url += ('&' + arg_name + '=' + value)
        logger.info('Dew Point: ' + value + 'degF')
            # logger.info('item: ' + key + ' - ' + str(parsed_json[key]))
            #if "time" == key:
        time = datetime.datetime.now(datetime.timezone.utc)
        arg_name = "dateutc"
        value = urllib.parse.quote_plus(time.strftime("%Y-%m-%d %H:%M:%S")) # YYYY-MM-DD HH:MM:SS
        wu_url += ('&' + arg_name + '=' + value)
        logger.info('url: '+ wu_url)

        try:
            resonse = urllib2.urlopen(wu_url)
        except urllib2.URLError as e:
            logger.error('URLError: ' + str(wu_url) + ': ' + str(e.reason))
            return None
        except:
            import traceback
            logger.error('Exception: ' + traceback.format_exc())
            return None
        resonse.close()

def on_publish(mosq, obj, mid):
    # logger.info("Published message with message ID: "+str(mid))
    pass


# Create the Mosquitto client
mqttclient = paho.Client(paho.CallbackAPIVersion.VERSION1)

# Bind the Mosquitte events to our event handlers
mqttclient.on_connect = on_connect
mqttclient.on_subscribe = on_subscribe
mqttclient.on_message = on_message
mqttclient.on_publish = on_publish


# Connect to the Mosquitto broker
logger.info("Connecting to broker " + config['broker_address'] + ":" + str(config['broker_port']))
if config['broker_user'] is not None:
    if config['broker_password'] is not None:
        mqttclient.username_pw_set(config['broker_user'],config['broker_password'])
    else:
        mqttclient.username_pw_set(config['broker_user'])
else:
    logger.info('No MQTT username and password set')
mqttclient.connect(config['broker_address'], config['broker_port'], 60)

# Start the Mosquitto loop in a non-blocking way (uses threading)
mqttclient.loop_forever()
