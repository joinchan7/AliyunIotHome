import context
from aliyun_iot_device.mqtt import Client as IOT
import time


PRODUCE_KEY = "a1XNizxeXZf"
DEVICE_NAME = "lock"
DEVICE_SECRET = "CyinTK0dMDXWsKLh8ByLHuqYAxi5Vd5z"
CLIENT_ID = ""

iot = IOT((PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET), transport="websockets")

iot.connect()

iot.loop_start()
while True:
    iot.publish('success', 1)
    time.sleep(5)
