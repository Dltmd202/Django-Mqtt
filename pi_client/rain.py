import time
import spidev
import paho.mqtt.client as mqtt
import json


class Rain:
    def __init__(self, ip="localhost"):
        self._client = None
        self.spi = spidev.SpiDev()
        self.rainlevel = 0
        self.ip = ip
        self.channel = 0

    @property
    def client(self):
        if self._client:
            return self._client
        else:
            client = mqtt.Client()

            def on_connect(client, userdata, flags, rc):
                print("Connected Rain Sensor" + str(rc))

            def on_publish(client, userdata, mid):
                msg_id = mid

            client.on_connect = on_connect
            client.on_publish = on_publish
            self._client = client
            return client

    def init_pin(self):
        self.spi.open(0, 0,)
        self.spi.max_speed_hz = 976000

    def readChannel(self, channel):
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        adc_out = ((adc[1] & 3) << 8) + adc[2]
        return adc_out

    def run(self):
        self.init_pin()
        self.client.connect(self.ip)
        self.client.loop_start()
        try:
            while True:
                self.rainlevel = self.readChannel(self.channel)
                msg = {
                    "msg": "success",
                    "rainlevel": str(self.rainlevel),
                    "status": 1
                }
                print(f"[sensor/rain] publish : {msg}")
                self.client.publish("sensor/rain", json.dumps(msg))
        except KeyboardInterrupt:
            print("Finished rain")
            self.client.loop_stop()
            self.client.disconnect()
            self.spi.close()


if __name__ == "__main__":
    rain = Rain()
    rain.run()
    