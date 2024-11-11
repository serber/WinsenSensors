# Class for reading data from Winsen ZE series sensors
# https://www.winsen-sensor.com/d/files/manual/ze07-co.pdf
# https://www.winsen-sensor.com/d/files/manual/ze08-ch2o.pdf
# https://www.winsen-sensor.com/d/files/manual/ze25-o3.pdf
# 2024-11-11 14:20:20

import machine
import time

class WinsenZESensorAnalog:
    DAC_MIN = const(0.4)
    DAC_MAX = const(2.0)

    def __init__(self, analog_pin, min_ppm, max_ppm, round, debug=False):
        self._adc = machine.ADC(machine.Pin(analog_pin, mode=machine.Pin.IN))
        self._min_ppm = min_ppm
        self._max_ppm = max_ppm
        self._round = round
        self._debug = debug

    def read(self):
        adc_value = self._adc.read_u16()
        voltage = adc_value * 3.3 / 65535
        
        if self._debug:
            print("\tadc value: {:.2f}, voltage: {:.2f} ".format(adc_value, voltage))

        # map 0.4-2.0V to min_ppm-max_ppm
        concentration = self.__map(voltage, WinsenZESensorAnalog.DAC_MIN, WinsenZESensorAnalog.DAC_MAX, self._min_ppm, self._max_ppm)

        if concentration < 0:
            return None

        return round(concentration / 10, self._round)

    def __map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

class WinsenZESensor:
    SENSOR_MODE_INITIATIVE = const(0x40)
    SENSOR_MODE_QA = const(0x41)

    def __init__(self, uart_id, tx_pin, rx_pin, baudrate=9600, mode=SENSOR_MODE_INITIATIVE, multiplier=1.0, debug=False):
        self._uart = machine.UART(uart_id, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))
        self._mode = mode
        self._multiplier = multiplier
        self._debug = debug

        self.__set_mode()

    def read(self):
        if self._mode == WinsenZESensor.SENSOR_MODE_INITIATIVE:
            return self.__read_initiative_mode()

        if self._mode == WinsenZESensor.SENSOR_MODE_QA:
            return self.__read_qa_mode()

        if self._debug:
            print("\tincorrect mode", self._mode)

        return None

    def __validate_response(self, response):
        length = len(response)
        if response is None or length != 9 or response[0] != 0xFF:
            return False

        checksum = 0
        for i in range(1, length - 1):
            checksum += response[i]
        checksum = (~checksum + 1) & 0xFF

        return checksum == response[8]

    def __set_mode(self):
        checksum = 0
        if self._mode == WinsenZESensor.SENSOR_MODE_INITIATIVE:
            checksum = 0x47
        if self._mode == WinsenZESensor.SENSOR_MODE_QA:
            checksum = 0x46

        request = bytearray([0xFF, 0x01, 0x78, self._mode, 0x00, 0x00, 0x00, 0x00, checksum])

        if self._debug:
            print('\tset mode', ' '.join([f'{b:02x}' for b in request]))

        self._uart.write(request)

    def __read_initiative_mode(self):
        if self._uart.any():
            response = self._uart.read(9)

            if self._debug:
                print('\tresponse', ' '.join([f'{b:02x}' for b in response]))

            if self.__validate_response(response):
                return ((response[4] * 256) + response[5]) * self._multiplier
        return None

    def __read_qa_mode(self):
        request = bytearray([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])
        self._uart.write(request)

        time.sleep(0.5)

        if self._uart.any():
            response = self._uart.read(9)

            if self._debug:
                print('\tresponse', ' '.join([f'{b:02x}' for b in response]))
            
            if self.__validate_response(response):
                return ((response[2] * 256) + response[3]) * self._multiplier

        return None