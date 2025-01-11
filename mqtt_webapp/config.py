import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    MQTT_BROKER_URL = os.environ.get('MQTT_BROKER_URL') or 'broker.hivemq.com'
    MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT') or 1883)