#!/usr/bin/env python3
import os
import sys

try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from enviroplus import gas
from subprocess import PIPE, Popen

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

def get_proximity():
    proximity = ltr559.get_proximity()
    return proximity

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])

# Get the raw temperate from the sensor
def get_temperature():
    raw_temp = bme280.get_temperature()
    return raw_temp

# Get the adjusted temperature
def get_adjusted_temperature(factor):
    cpu_temps = [get_cpu_temperature()] * 5
    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    
    if factor > 0:
        adjusted_tmp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
    else:
        adjusted_tmp = raw_temp

    return adjusted_tmp

def get_pressure():
    data = bme280.get_pressure()
    return data

def get_humidity():
    humidity = bme280.get_humidity()
    dewpoint = get_temperature() - ((100 - humidity) / 5)
    corr_humidity = 100 - (5 * (get_adjusted_temperature - dewpoint))
    return min(100, corr_humidity)

def get_light():
    proximity = get_proximity()
    
    if proximity < 10:
        data = ltr559.get_lux()
    else:
        data = 1
    return data

def get_oxidising():
    data = gas.read_all()
    data = data.oxidising / 1000
    return data

def get_reducing():
    data = gas.read_all()
    data = data.reducing / 1000
    return data

def get_nh3():
    data = gas.read_all()
    data = data.nh3 / 1000
    return data