from .broker import ServerApplication
import threading

print("hi")

service = ServerApplication()
t = threading.Thread(target=service.run)
t.start()

