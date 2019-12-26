import context
from aliyun_iot_device.mqtt import Client as IOT
import time
from multiprocessing import Process, Value
import json
import RPi.GPIO as GPIO
import smbus


def on_connect(client, userdata, flags, rc):
    print('subscribe')
    client.subscribe(qos=1)


def on_message(client, userdata, msg):
    print('receive message')
    print(str(msg.payload))

    key = json.loads(msg.payload)['params']

    if 'Lock_control' in key:
        lock_control(key)
    elif 'LightLuminance' in key:
        led_control(key)
    elif 'CurtainOperation' in key:
        if(key['CurtainOperation'] == 1):
            sensor_control()
        else:
            pass
    elif 'cts' in key:
        print(key)
        curtain_control(key)
    elif 'StayAlarmSwitch' in key:
        alarm_control(key)


def alarm_control(key):
    val = key['StayAlarmSwitch']

    topic = '/sys/'+PRODUCE_KEY+'/' + DEVICE_NAME+'/thing/event/property/post'
    payload_json = {
        'id': int(time.time()),
        'params': {
            'StayAlarmSwitch': val  # int
        },
        'method': "thing.event.property.post"
    }
    iot.publish(topic=topic, payload=str(payload_json))

    global num2
    num2 = val
    num2 = Value("d", num2)


def alarm_child(num2):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    PIN1 = 18
    PIN2 = 17
    GPIO.setup(18, GPIO.IN)
    GPIO.setup(17, GPIO.OUT)
    time.sleep(2)
    while True:
        i = int(num2.value)
        if(i == 0):
            pass
        else:
            if GPIO.input(PIN1) == True:
                for _ in range(1, 6):
                    GPIO.output(PIN2, GPIO.LOW)
                    time.sleep(0.5)
                    GPIO.output(PIN2, GPIO.HIGH)
                    time.sleep(0.5)
            else:
                GPIO.output(PIN2, GPIO.HIGH)
            time.sleep(2)


def sensor_control():
    sensor_pin = 4
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sensor_pin, GPIO.IN)
    while True:
        # bug:监视了传感器的值后会一直执行,需求是只执行一次
        # 思路:1.如果传感器GPIO.input(sensor_pin)值改变则执行
        #     2.在变量i发生变化的时候主动通知

        if GPIO.input(sensor_pin) == 1:
            key = {'cts': 1}
            curtain_control(key)
        else:
            key = {'cts': 0}
            curtain_control(key)
        time.sleep(1)
        print(GPIO.input(sensor_pin))


def curtain_control(key):
    def setStep(w1, w2, w3, w4):
        GPIO.output(IN1, w1)
        GPIO.output(IN2, w2)
        GPIO.output(IN3, w3)
        GPIO.output(IN4, w4)

    def forward(delay, steps):
        for _ in range(0, steps):
            setStep(1, 0, 1, 0)
            time.sleep(delay)
            setStep(0, 1, 1, 0)
            time.sleep(delay)
            setStep(0, 1, 0, 1)
            time.sleep(delay)
            setStep(1, 0, 0, 1)
            time.sleep(delay)

    def backward(delay, steps):
        for _ in range(0, steps):
            setStep(1, 0, 0, 1)
            time.sleep(delay)
            setStep(0, 1, 0, 1)
            time.sleep(delay)
            setStep(0, 1, 1, 0)
            time.sleep(delay)
            setStep(1, 0, 1, 0)
            time.sleep(delay)

    def setUp():
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(IN1, GPIO.OUT)
        GPIO.setup(IN2, GPIO.OUT)
        GPIO.setup(IN3, GPIO.OUT)
        GPIO.setup(IN4, GPIO.OUT)

    IN1 = 26
    IN2 = 19
    IN3 = 13
    IN4 = 6
    setUp()
    val = key['cts']
    if val == 0:
        backward(0.001, 860)
    else:
        forward(0.001, 860)


def lock_control(key):
    val = key['Lock_control']

    topic = '/sys/'+PRODUCE_KEY+'/' + DEVICE_NAME+'/thing/event/property/post'
    payload_json = {
        'id': int(time.time()),
        'params': {
            'Lock_control': val
        },
        'method': "thing.event.property.post"
    }
    iot.publish(topic=topic, payload=str(payload_json))

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    In_Pin = 21
    GPIO.setup(In_Pin, GPIO.OUT, initial=GPIO.LOW)
    pwm = GPIO.PWM(In_Pin, 50)
    pwm.start(0)

    if val == 0:
        r = 0
    else:
        r = 180
    pwm.ChangeDutyCycle(2.5+r/360*20)
    time.sleep(1)


def led_control(key):
    val = key['LightLuminance']

    topic = '/sys/'+PRODUCE_KEY+'/' + DEVICE_NAME+'/thing/event/property/post'
    payload_json = {
        'id': int(time.time()),
        'params': {
            'LightLuminance': val  # int
        },
        'method': "thing.event.property.post"
    }
    iot.publish(topic=topic, payload=str(payload_json))

    global num
    num = val
    num = Value("d", num)


def led_child(num):
    pin = 20
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    pwm = GPIO.PWM(pin, 80)
    pwm.start(0)

    while True:
        i = int(num.value)
        pwm.ChangeDutyCycle(i)
        time.sleep(0.2)


def ht_upload():
    i2c = smbus.SMBus(1)
    addr = 0x44
    i2c.write_byte_data(addr, 0x23, 0x34)
    time.sleep(0.5)
    i2c.write_byte_data(addr, 0xe0, 0x0)
    data = i2c.read_i2c_block_data(addr, 0x0, 6)
    rawT = ((data[0]) << 8) | (data[1])
    rawR = ((data[3]) << 8) | (data[4])
    temp = round(-45 + rawT * 175 / 65535, 2)  # float
    hum = round(100 * rawR / 65535)  # int
    time.sleep(3)

    topic = '/sys/'+PRODUCE_KEY+'/' + DEVICE_NAME+'/thing/event/property/post'
    payload_json = {
        'id': int(time.time()),
        'params': {
            'CurrentHumidity': hum,
            'CurrentTemperature': temp
        },
        'method': "thing.event.property.post"
    }
    return topic, payload_json


PRODUCE_KEY = "a1XNizxeXZf"
DEVICE_NAME = "my_home"
DEVICE_SECRET = "velAIa2mV8eZKn6T2fucvpRuJY5EUdVT"

num = Value("d", 0)
p = Process(target=led_child, args=(num,))
p.start()

num2 = Value("d", 0)
p2 = Process(target=alarm_child, args=(num2,))
p2.start()

iot = IOT((PRODUCE_KEY, DEVICE_NAME, DEVICE_SECRET))


iot.on_connect = on_connect
iot.on_message = on_message

iot.connect()

iot.loop_start()
if __name__ == "__main__":
    try:
        while True:
            topic, payload_json = ht_upload()
            iot.publish(topic=topic, payload=str(payload_json), qos=1)
            time.sleep(5)
    except:
        p.terminate()
        p2.terminate()
        print('stop')
