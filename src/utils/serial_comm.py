from __future__ import annotations
import threading

from typing import Optional
from serial import Serial, serial_for_url  # pyserial

from utils.singleton import Singleton


class SerialComm(metaclass=Singleton):
    def __init__(self, port: str = "loop://", baudrate: int = 9600, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._lock = threading.Semaphore()
        self._ser = None  # lazy

    def _ensure_open(self):
        if self._ser is not None:
            return
        if Serial is None and serial_for_url is None:
            self._ser = False
            return
        try:
            if str(self.port).startswith("loop://"):
                self._ser = serial_for_url(self.port, baudrate=self.baudrate, timeout=self.timeout)
            else:
                self._ser = Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
        except Exception:
            self._ser = False

    def send(self, msg: str):
        self._ensure_open()
        if not self._ser:
            return  # no-op
        with self._lock:
            self._ser.write(msg.encode())

    def receive(self) -> Optional[str]:
        self._ensure_open()
        if not self._ser:
            return None
        with self._lock:
            if self._ser.in_waiting > 0:
                data = self._ser.readline().decode(errors="ignore").strip()
                return data or None
            return None

    def close(self):
        if getattr(self, "_ser", None) and self._ser not in (None, False):
            try:
                self._ser.close()
            except Exception:
                pass
            finally:
                self._ser = None
