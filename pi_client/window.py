import time

import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import json


class Window:
    def __init__(self, ip="localhost"):
        self._client = None
        self.ip = ip
        self.mpin = 12
        self.servo_pwm = None

    @property
    def client(self):
        if self._client:
            return self._client
        else:
            client = mqtt.Client()

            def on_connect(client, userdata, flags, rc):
                print("Connected Window_Control " + str(rc))
                client.subscribe("control/moter")

            def on_message(client, userdata, msg):
                print(f"!![{msg.topic}] sub : {msg.payload}")
                self.control_window(msg)

            client.on_connect = on_connect
            client.on_message = on_message
            self._client = client
            return client

    def init_pin(self):
        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)
        gpio.setup(self.mpin, gpio.OUT)
        self.servo_pwm = gpio.PWM(self.mpin, 50)
        self.servo_pwm.start(0)

    def control_window(self, msg):
        print("[control/moter] sub : move")
        state = json.loads(msg.payload)["is_open"]
        if state == True:
            print("open")
            self.open()
        else:
            print("close")
            self.close()

    def open(self):
        self.servo_pwm.ChangeDutyCycle(10)

    def close(self):
        self.servo_pwm.ChangeDutyCycle(2)

    def run(self):
        self.client.connect(self.ip)
        self.init_pin()
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("Finished window!")
            self.client.unsubscribe("control/moter")
            self.client.disconnect()
            gpio.cleanup()


if __name__ == "__main__":
    Moter_Control = Window()
    Moter_Control.run()
