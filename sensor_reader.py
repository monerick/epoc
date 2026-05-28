import time
import math
import random
import logging
import threading

from config import Config

logger = logging.getLogger(__name__)


class SensorReader:
    def __init__(self, data_store, callback=None):
        self.data_store = data_store
        self.callback = callback
        self._running = False
        self._thread = None
        self._gpio_available = False
        self._sensor = None
        self._simulated = not Config.PI_OPTIMIZED

    def _init_gpio(self):
        if not Config.PI_OPTIMIZED:
            logger.info("Modo simulacion: no hay GPIO disponible en este sistema")
            return False
        try:
            import RPi.GPIO as GPIO
            import Adafruit_DHT
            self._gpio_available = True
            self._GPIO = GPIO
            self._DHT = Adafruit_DHT
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            logger.info(f"Sensor GPIO inicializado: pin {Config.SENSOR_PIN}, tipo {Config.SENSOR_TYPE}")
            return True
        except ImportError as e:
            logger.warning(f"Libreria GPIO no instalada ({e}). Usando modo simulacion.")
            logger.warning("Instale: pip install RPi.GPIO Adafruit_DHT")
            return False
        except Exception as e:
            logger.error(f"Error iniciando GPIO: {e}")
            return False

    def _read_gpio(self):
        try:
            sensor_map = {"dht22": self._DHT.DHT22, "dht11": self._DHT.DHT11, "am2302": self._DHT.AM2302}
            sensor_type = sensor_map.get(Config.SENSOR_TYPE, self._DHT.DHT22)
            humidity, temperature = self._DHT.read_retry(sensor_type, Config.SENSOR_PIN)
            if humidity is not None and temperature is not None:
                return {"temperature": round(temperature, 2), "humidity": round(humidity, 2)}
            logger.warning("Lectura GPIO fallo, retornando None")
            return None
        except Exception as e:
            logger.error(f"Error leyendo sensor GPIO: {e}")
            return None

    def _read_simulated(self):
        t = time.time()
        temp = 22.0 + 5.0 * math.sin(t * 0.05) + random.uniform(-0.5, 0.5)
        hum = 60.0 + 10.0 * math.sin(t * 0.03 + 1.0) + random.uniform(-1.0, 1.0)
        return {"temperature": round(temp, 2), "humidity": round(humidity, 2)}

    def _loop(self):
        logger.info(f"Lector de sensores iniciado (intervalo={Config.SENSOR_INTERVAL}s)")
        index = 0
        while self._running:
            try:
                if self._gpio_available:
                    raw = self._read_gpio()
                else:
                    raw = self._read_simulated()

                if raw:
                    t = time.strftime("%H:%M:%S")
                    self.data_store.add_point(index, raw["temperature"])
                    if self.callback:
                        self.callback(raw)
                    logger.debug(f"Sensor [{index}]: {raw['temperature']}C, {raw['humidity']}%")
                    index += 1
            except Exception as e:
                logger.error(f"Error en loop de sensor: {e}")

            time.sleep(Config.SENSOR_INTERVAL)

    def start(self):
        if self._running:
            return
        self._init_gpio()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="sensor-reader")
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        if self._gpio_available:
            try:
                self._GPIO.cleanup()
            except Exception:
                pass
        logger.info("Lector de sensores detenido")
