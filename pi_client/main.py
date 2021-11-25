from detect import PIR
from distance import Distance
from temp import Temp_Hum

import threading

if __name__ == "__main__":
    pir = PIR("localhost")
    dist = Distance("localhost")
    temp = Temp_Hum("localhost")

    pir_th = threading.Thread(target=pir.run)
    dist_th = threading.Thread(target=dist.run)
    temp_th = threading.Thread(target=temp.run)
