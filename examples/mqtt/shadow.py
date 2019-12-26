import context
from aliyun_iot_device.mqtt import Client as IOT
import time


def on_connect(client, userdata, flags, rc):
    print('subscribe')
    client.subscribe(topic='shadow', qos=1)


def on_message(client, userdata, msg):
    print('receive message')
    print(str(msg.payload))


PRODUCE_KEY = "a1XNizxeXZf"
DEVICE_NAME = "lock"
DEVICE_SECRET = "CyinTK0dMDXWsKLh8ByLHuqYAxi5Vd5z"

iot = IOT((PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET))

iot.on_connect = on_connect
iot.on_message = on_message

iot.connect()

i = 1
iot.loop_start()
while True:
    iot.publish(payload={"method": "update", "version": i,
                         "reported": {"online": True}}, topic="shadow", qos=1)
    i += 1
    time.sleep(5)
