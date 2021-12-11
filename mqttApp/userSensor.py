import time
import paho.mqtt.client as mqtt
import json
import os


class UserSensor:
    def __init__(self, IP="172.20.10.8"):
        self._client = None
        self.IP = IP

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

    def run(self, order):
        self.client.connect(self.IP)
        self.client.loop_start()
        try:
            msg = {
                "order": order
            }
            self.client.publish("sensor/user", json.dumps(msg))
            print(f"publishing : {msg}")
        except KeyboardInterrupt:
            print("Finished")
            self.client.loop_stop()
            self.client.disconnect()


if __name__ == "__main__":
    pass
