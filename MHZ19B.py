# Class for reading data from MHZ19B sensor
# https://www.winsen-sensor.com/d/files/manual/mh-z19b.pdf
# 2024-10-27 21:58:22

import machine
import time

class MHZ19B:
    def __init__(self, uart_id, tx_pin, rx_pin, baudrate=9600):
        self._uart = machine.UART(uart_id, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))

    def read_co2(self):
        request = bytearray([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
        self._uart.write(request)
        
        time.sleep(0.1)

        if self._uart.any():
            response = self._uart.read(9)
            if self.__validate_response(response):
                return response[2] * 256 + response[3]
        return None
    
    def calibrate(self, led_pin):
        led = machine.Pin(led_pin, machine.Pin.OUT)

        print("Please wait for 20 minutes in clean air")

        for _ in range(11):
            led.toggle()
            time.sleep(0.5)

        print("Waiting 20 minutes")

        time.sleep(1200)

        print("Starting calibration")

        request = bytearray([0xFF, 0x01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78])
        self._uart.write(request)

        print("Calibration command sent")

    def __validate_response(self, response):
        if response is None or len(response) != 9 or response[0] != 0xFF or response[1] != 0x86:
            return False
        
        checksum = 0
        length = len(response)
        
        for i in range(1, length - 1):
            checksum += response[i]
        checksum = (~checksum + 1) & 0xFF
        
        return checksum == response[8]