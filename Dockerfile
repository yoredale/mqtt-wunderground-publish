FROM python:3.9.0-alpine3.12

# Configuration
ENV MQTT_URL "tcp://localhost:8883"
# ENV CONFIG_TOPIC=<MQTT topic> # example sensors/rtl_433/something
# ENV CONFIG_WU_ID=<weather underground station id
# ENV CONFIG_WU_KEY=<weather underground key/password>

RUN pip install paho-mqtt

ADD publish.py /
CMD ["python", "/publish.py"]
