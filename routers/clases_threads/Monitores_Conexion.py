from threading import Thread, Event
from Recorders import PeriodicRecorder
import time as tm
import requests as rq


class Monitor:
    def __init__(
        self,
        url: str = "https://www.flightradar24.com/23.42,-79.95/6",
        time_out: int = 15,
    ):
        self.url = url
        self.time_out = time_out

    """ Esta clase es una base para crear clases q monitoreen la conexion"""

    # Verifica y controla la conexion a internet
    def check_connection(self):
        try:
            rq.get(self.url, timeout=self.time_out)
            return True
        except rq.exceptions.RequestException:
            return False


class MonitorThread(Monitor, Thread):
    def __init__(
        self,
        thread: PeriodicRecorder,
        url: str = "https://www.flightradar24.com/23.42,-79.95/6",
        time_wait: int = 5,
        time_out: int = 15,
    ):
        super().__init__(url, time_out)
        Thread.__init__(self)
        self.thread = thread
        self.time_wait = time_wait
        self.stop_thread = Event()

    """Monitor thread es una clase creada especialmente para este proyecto 
mediante la url a la cual le haremos la grabacion determina si hay conexion y da inicio al hilo de grabacion 
en caso de q haya pasdo un periodo de tiempo sin encontrar la conexion este detendra el hilo de grabacion existente y dara inicio a uno nuevo """

    def stop(self):
        if self.thread.is_alive():
            self.thread.stop()
            self.thread.join()
        self.stop_thread.set()

    # Da inicio al hilo q maneja o crea uno nuevo
    def run(self):
        count = 0
        while not self.stop_thread.is_set():
            if self.check_connection():
                print("Connection finded!!!!!!")
                count = 0
                if not self.thread.is_alive():
                    self.thread.start()
            else:
                print("Search connection")
                count += 1
                if count == 4:
                    if self.thread.is_alive():
                        self.thread.stop()
                        self.thread.join()
                        self.thread = PeriodicRecorder(
                            url=self.thread.url,
                            interval_seconds=self.thread.interval_seconds,
                        )
            tm.sleep(self.time_wait)
        print("hilo monitor detenido")


class MonitorControl:
    def __init__(self):
        self.monitor = None
        self.detenido = False

    """ Esta clase nos a permitir controlar al monitor desde los endpoints, dandole inicio y deteniendo el proceso """

    def iniciar(
        self,
        thread: PeriodicRecorder,
        url: str = "https://www.flightradar24.com/23.42,-79.95/6",
        time_wait: int = 5,
        time_out: int = 15,
    ):
        self.monitor = MonitorThread(
            thread=thread, url=url, time_wait=time_wait, time_out=time_out
        )
        self.monitor.start()

    def detener(self):
        if self.monitor:
            self.monitor.stop()
            self.monitor.join()
            self.detenido = True
