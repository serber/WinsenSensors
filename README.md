# Winsen ZE series & MHZ19B sensors app
MicroPython code to work with Winsen sensors via UART or DAC

### MHZ19B
#### Read data from sensor
```python
mhz19b = MHZ19B(uart_id=1, tx_pin=8, rx_pin=9)
while True:
 co2 = mhz19b.read_co2()
 if co2 is not None:
     print("CO2:", co2, "ppm")
 else:
     print("Failed to read data from sensor")

 time.sleep(2)
```

#### Calibration
In some cases sensor calibration may be required (for example, `read_co2` method always return 5000 ppm)
> Calibration should be performed outdoors

Use `calibrate` method for that (only once)
```python
mhz19b = MHZ19B(uart_id=1, tx_pin=8, rx_pin=9)
mhz19b.calibrate(led_pin=25)
```

### ZE series sensors
#### Read data from sensor
```python
ze25o3 = WinsenZESensor(uart_id=0, tx_pin=0, rx_pin=1, multiplier=0.0001, debug=True)
ze25o3_analog = WinsenZESensorAnalog(analog_pin=26, min_ppm=0.0, max_ppm=10.0, round=2, debug=True)

while True:
 o3 = ze25o3.read()
 o3_analog = ze25o3_analog.read()

 if o3 is not None:
     print("O3:", o3, "ppm")
 else:
     print("Failed to read data from sensor")
     
 if o3_analog is not None:
     print("O3 analog:", o3_analog, "ppm")
 else:
     print("Failed to read data from sensor")
```