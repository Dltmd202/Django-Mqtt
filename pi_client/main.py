import os

from detect import PIR
from distance import Distance
from temp import Temp_Hum
from broker import ServerApplication

import multiprocessing


class Client:
    def __init__(self, ip="localhost"):
        self.ip = ip
        self.pir = PIR(ip)
        self.dist = Distance(ip)
        self.temp = Temp_Hum(ip)
        self.broker = ServerApplication()
        self.sensors = [self.pir, self.dist, self.temp, self.broker]
        self.processingQ = []

    def run(self):
        print(self.ip)
        for sensor in self.sensors:
            p = multiprocessing.Process(target=sensor.run)
            self.processingQ.append(p)
            p.start()
            print(p, "start")

        try:
            for process in self.processingQ:
                process.join()
        except KeyboardInterrupt:
            for process in self.processingQ:
                process.terminate()


if __name__ == "__main__":
    client = Client(os.environ.get("BROCKER", "localhost"))
    client.run()
