from .detect import PIR
from .distance import Distance
from .temp import Temp_Hum

pir = PIR()
dist = Distance()
temp = Temp_Hum()

pir.run()
dist.run()
temp.run()
