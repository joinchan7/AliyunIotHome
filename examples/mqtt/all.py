# -*- coding: utf-8 -*-

__author__ = "yansongda <me@yansongda.cn>"

import context
from aliyun_iot_device.mqtt import Client as IOT
import time
import re
import RPi.GPIO as GPIO


def on_connect(client, userdata, flags, rc):
    print('subscribe')
    client.subscribe(qos=1)


def on_message(client, userdata, msg):
    print('receive message')
    print(str(msg.payload))
    lock_control(msg)


def lock_control(msg):
    # 门锁状态控制
    val = re.findall(r'\"Lock_control\":\d', str(msg.payload))
    status = str(val)[17]
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    In_Pin=21
    GPIO.setup(In_Pin,GPIO.OUT,initial=GPIO.LOW)
    p=GPIO.PWM(In_Pin,50)
    p.start(0) 
    try:
        if(int(status)==0):
            r=0
        else:
            r=180
        p.ChangeDutyCycle(2.5+r/360*20)
        time.sleep(1)
    except:
        pass


PRODUCE_KEY = "a1XNizxeXZf"
DEVICE_NAME = "lock"
DEVICE_SECRET = "CyinTK0dMDXWsKLh8ByLHuqYAxi5Vd5z"

iot = IOT((PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET))

iot.on_connect = on_connect
iot.on_message = on_message

iot.connect()

iot.loop_start()
while True:
    iot.publish(payload="success", qos=1)
    time.sleep(5)
