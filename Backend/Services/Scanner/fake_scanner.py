# Fake scanner for testing and developing

from enum import Enum
import random
import time
from typing import Tuple

scanned_string="FAKE QR CODE"


class ScannerStatus(Enum):
    DEVICE_NOT_FOUND = "Device not found"
    NO_DEVICE = "No device"
    READ_ERROR = "Read error"
    READ_OK = "Read ok"
    
class Scanner:
    def __init__(self, vendor_id=None, product_id=None)-> None:
        self.device = "Fake device" if vendor_id and product_id else None

    def read_barcode(self, callback=None)-> Tuple[ScannerStatus, str|None]:
        try:
            time.sleep(2)
            random_number = random.randint(0, 99)
            ss = f"{scanned_string}, rand = {str(random.randint(0, 99))}"
            if callback:
                callback(scanned_string=ss)
            return ScannerStatus.READ_OK, ss
        except Exception as e:
            return ScannerStatus.READ_ERROR, None