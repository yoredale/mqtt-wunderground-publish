# MQTT Wunderground Publish

Publishes personal weather station data recieved from a MQTT topic to Weather Underground.

This was developed to work with [rtl-433](https://github.com/merbanan/rtl_433) and a La Crosse Breeze Pro station.

Required environment variables
```txt
MQTT_URL "tcp://localhost:8883"
CONFIG_TOPIC=<MQTT topic> # example sensors/rtl_433/something
CONFIG_WU_ID=<weather underground station id
CONFIG_WU_KEY=<weather underground key/password>
```

## MQTT Topic Format

The payload of the message needs to be in the following format:
```json
{
    "time":"2020-11-16T02:08:20",
    "temperature_F":38.48,
    "humidity":88,
    "wind_avg_mi_h":0,
    "wind_dir_deg":9,
}
```

