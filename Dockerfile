FROM python:3.9.0-alpine3.12

# Configuration
ENV MQTT_URL "tcp://localhost:1883"
ENV MQTT_USR "username"
ENV MQTT_PWD "password"
ENV CONFIG_TOPIC "application/AP-ID/device/DEV-EUI/event/up"
ENV CONFIG_WU_ID "WU-ID"
ENV CONFIG_WU_KEY "WU-KEY"

RUN pip install paho-mqtt

ADD publish.py /
CMD ["python", "/publish.py"]
