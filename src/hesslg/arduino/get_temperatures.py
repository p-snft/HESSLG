#!/usr/bin/env python
import datetime
import numpy as np
import time
import serial

upper_temperatures = np.array([
    40,
    40,
    150,
    150,
])

lower_temperatures = np.array([
    0,
    0,
    0,
    0,
])


def get_temperatures():
    ser = serial.Serial(
        port="/dev/ttyACM0", 
        baudrate = 9600,
        timeout=1,
    )

    x = ser.read(160)
    x = x.decode('UTF-8')

    for line in x.split('\n')[::-1]:
        vals = line.split(",")
        vals = [val.strip() for val in vals]
        if len(vals) == 8:
        	adc_count = np.array([int(val) for val in vals[::2]])
        	voltage = np.array([float(val) for val in vals[1::2]])
        	break

    # rather large tollerance because assert is meant for read-in errors
    assert np.allclose(voltage, adc_count/1024*5.0, rtol=0.1)

    temperatures = adc_count/1024*5.0*(upper_temperatures-lower_temperatures)/10.0

if __name__ == "__main__":
    timestamp = datetime.datetime.now().astimezone().isoformat()
    print("{},{:.2f},{:.2f},{:.2f},{:.2f}".format(timestamp, *temperatures))

