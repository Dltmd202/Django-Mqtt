from .broker import ServerApplication
import threading


service = ServerApplication()
t = threading.Thread(target=service.run)
t.start()

