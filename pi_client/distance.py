import paho.mqtt.client as mqtt
import RPi.GPIO as gpio
import time
import json


class Distance:
    def __init__(self, ip="localhost"):
        self.distance = 0
        self.ip = ip
        self._client = None
        self.trig_pin = 20  # 초음파 센서 trig gpio핀 값
        self.echo_pin = 21  # 초음파 센서 echo gpio핀 값

    @property
    def client(self):  # 클라이언트 private로 생성
        if self._client:
            return self._client
        else:
            client = mqtt.Client()

            def on_connect(client, userdata, flags, rc):
                print("Connected Ultrasonic sensor" + str(rc))

            def on_publish(client, userdata, mid):
                msg_id = mid

            client.on_connect = on_connect
            client.on_publish = on_publish
            self._client = client
            return client

    def init_gpio(self):  # gpio핀 초기 설정
        gpio.setmode(gpio.BCM)
        gpio.cleanup()
        gpio.setup(self.trig_pin, gpio.OUT)  # 초음파센서 trig핀 설정
        gpio.setup(self.echo_pin, gpio.IN)  # 초음파센서 echo핀 설정

    def get_distance(self):  # 초음파 센서 거리 구하는 함수
        gpio.output(self.trig_pin, False)
        time.sleep(1)
        gpio.output(self.trig_pin, True)
        time.sleep(0.00001)
        gpio.output(self.trig_pin, False)
        while gpio.input(self.echo_pin) == 0:  # 펄스신호가 들어올때 시작하는 시간측정
            pulse_start = time.time()
        while gpio.input(self.echo_pin) == 1:  # 퍼스신호가 떨어질때 끝나는 시간측정
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start  # 초음파 왕복 시간 계산
        distance = pulse_duration * 34000 / 2  # 시간과 초음파 속도를 이용해서 거리 계산
        distance = round(distance, 2)
        return distance

    def run(self):
        self.init_gpio()
        self.client.connect(self.ip)  # 로컬로 접속
        self.client.loop_start()
        try:
            while True:
                self.distance = self.get_distance()  # 초음파센서 거
                msg = {
                    "distance": self.distance  # 송신할 거리값 메시지
                }
                self.client.publish("sensor/distance", json.dumps(msg))  # json형식으로 송신
                print(f"publishing : {msg}")  # 송신한 메시지 출력
                time.sleep(1)
        except KeyboardInterrupt:
            print("Finished distance!")
            self.client.loop_stop()
            self.client.disconnect()
            gpio.cleanup()


if __name__ == "__main__":
    dis = Distance()
    dis.run()
