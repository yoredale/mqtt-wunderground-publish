# MQTT Wunderground Publish

Publishes personal sensor data recieved from a MQTT topic to Weather Underground.

This takes the data from a Senzemo Senstick, as published by chirpstack to an mqtt broker.


Required environment variables
```txt
MQTT_URL="tcp://localhost:1883"
CONFIG_TOPIC=<MQTT topic> # eg application/APP_ID/device/DEV_EUI/event/up
CONFIG_WU_ID=<weather underground station id>
CONFIG_WU_KEY=<weather underground key/password>
```
Optional variables to do mqtt authentication
```txt
MQTT_USR="Username"
MQTT_PWD="Password"
```

## MQTT Topic Format

The relevant payload of the message output by the chirpstack decoder for the senstick has the following format:
```json
{
  "time":"2020-11-16T02:08:20",
  "objects":
    {
      "temperature":15,
      "humidity":88,
      "pressure":976.5
    }
}
```
Temperature is deg C, Humidity is %, Pressure is hPa.

Dewpoint is calculated, temperature and dew point are converted to Farenheit for upload.

Pressure is converted to Mean Sea Level Pressure, then converted to Inches of Mercury.

