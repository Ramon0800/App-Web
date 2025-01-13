from io import BytesIO
from threading import Thread
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from PIL import Image
import cv2
import time as tm
import numpy as np
import requests
import zipfile


class Recorder:
    def __init__(
        self,
        PATH_TO_VIDEO: str = "output.mp4",
        INTERVAL: int = 5,
        frames: float = 10.0,
        width: int = 1770,
        heigth: int = 720,
    ):
        self.PATH = PATH_TO_VIDEO
        self.interval = INTERVAL
        self.frame = frames
        self.width = width
        self.height = heigth
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.out = cv2.VideoWriter(
            timestamp + "_" + self.PATH, fourcc, self.frame, (self.width, self.height)
        )
        self.frame_count = 0

    def stop(self):
        self.out.release()
        print(
            f"[RELEASED] Saved video with {self.frame_count} frames at {self.frame} FPS"
        )

    def release(self):
        # write video data
        self.out.release()
        print(
            f"[RELEASED] Saved video with {self.frame_count} frames at {self.frame} FPS"
        )

        # set up new video file
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.out = cv2.VideoWriter(
            timestamp + "_" + self.PATH, fourcc, self.frame, (self.width, self.height)
        )
        self.frame_count = 0


class PeriodicRecorder(Recorder, Thread):
    def __init__(
        self,
        url: str = "https://www.flightradar24.com/23.42,-79.95/6",
        PATH_TO_VIDEO: str = "output.mp4",
        INTERVAL: int = 5,
        frames: float = 10.0,
        width: int = 1770,
        heigth: int = 720,
    ):
        super().__init__(PATH_TO_VIDEO, INTERVAL, frames, width, heigth)
        Thread.__init__(self)
        self.url = url
        edge_options = Options()
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        """try:
           service=Service(EdgeChromiumDriverManager().install()) 
       except requests.exceptions.ConnectionError:
           print('Error de coneccion')
       except zipfile.BadZipFile:
           print('Esta descarga no es valida puede que tenga un error en la descarga o el archivo no es un zip')"""
        service = Service("C:\THALIA\Webdrivers\E131\msedgedriver.exe")
        self.driver = webdriver.Edge(service=service, options=edge_options)

    def screenshoot(self):
        img = self.driver.get_screenshot_as_png()
        img = Image.open(BytesIO(img))
        img_np = np.asarray(img)
        img_np = img_np[310:520, 350:870]
        offset_x = 0
        offset_y = 0
        img_np = img_np[offset_y : offset_y + 720, offset_x : offset_x + 1770, :]
        img_np = cv2.resize(img_np, (self.width, self.height))
        return img_np

    def stop(self):
        self.out.release()
        print(
            f"[RELEASED] Saved video with {self.frame_count} frames at {self.frame} FPS"
        )
        self.driver.quit()

    def run(self):
        contador = 0
        print("Start the flightradar24 app in 5 seconds")
        self.driver.get(self.url)
        self.driver.set_window_size(1200, 800)
        tm.sleep(10)
        try:
            cookie_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Continue']"))
            )
            cookie_button.click()
            print("Banner de cookies manejadas correctamente")
            while True:
                img_np = self.screenshoot()
                # Write the __frame to the video file
                self.out.write(cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR))
                self.frame_count += 1
                contador = self.frame_count
                print(f"[NEW FRAME ADDED] Recorded {self.frame_count} frames in total")
                if contador == (1200 // self.interval):
                    self.driver.refresh()
                    tm.sleep(10)
                    contador = 0
                    print("refrescado")

                    # waits for the time interval between frames to be over
                tm.sleep(self.interval)
        except Exception as e:
            print(f"Este error a ocurrido:{e}")
        except NoSuchElementException:
            print(f"No se encontro el elemento")
