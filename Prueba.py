import Monitores_Conexion as cm
import Recorders as cr
import time as tm

RECORDING_TIME = 8 * 60 * 60
url = "https://www.flightradar24.com/23.42,-79.95/6"
interval_seconds = 60
worker = cr.PeriodicRecorder(
    url=url, INTERVAL=interval_seconds, recording_time=RECORDING_TIME
)
monitor = cm.MonitorThread(thread=worker, url=url, time_wait=20)
monitor.daemon = True
monitor.start()
tm.sleep(RECORDING_TIME)
worker.release()
tm.sleep(RECORDING_TIME)
print("finish")
