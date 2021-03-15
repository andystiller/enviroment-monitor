#!/usr/bin/env python3

import time
import colorsys
import os
import sys
import ST7735

from subprocess import PIPE, Popen
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont
import logging
import config
import sensors

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""all-in-one.py - Displays readings from all of Enviro plus' sensors
Press Ctrl+C to exit!
""")

# Create ST7735 LCD display class
st7735 = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display
st7735.begin()

WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
path = os.path.dirname(os.path.realpath(__file__))
font_size = 20
font = ImageFont.truetype(UserFont, font_size)

message = ""

# The position of the top bar
top_pos = 25


# Displays data and text on the 0.96" LCD
def display_text(variable, data, unit):
    # Maintain length of list
    values[variable] = values[variable][1:] + [data]
    # Scale the values for the variable between 0 and 1
    vmin = min(values[variable])
    vmax = max(values[variable])
    colours = [(v - vmin + 1) / (vmax - vmin + 1) for v in values[variable]]
    # Format the variable name and value
    message = "{}: {:.1f} {}".format(variable[:4], data, unit)
    logging.info(message)
    draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))
    for i in range(len(colours)):
        # Convert the values to colours from red to blue
        colour = (1.0 - colours[i]) * 0.6
        r, g, b = [int(x * 255.0) for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]
        # Draw a 1-pixel wide rectangle of colour
        draw.rectangle((i, top_pos, i + 1, HEIGHT), (r, g, b))
        # Draw a line graph in black
        line_y = HEIGHT - (top_pos + (colours[i] * (HEIGHT - top_pos))) + top_pos
        draw.rectangle((i, line_y, i + 1, line_y + 1), (0, 0, 0))
    # Write the text at the top in black
    draw.text((0, 0), message, font=font, fill=(0, 0, 0))
    st7735.display(img)

delay = 0.5  # Debounce the proximity tap
mode = 0  # The starting mode
last_page = 0
light = 1

# Create a values dict to store the data
variables = ["temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3"]

values = {}

for v in variables:
    values[v] = [1] * WIDTH

# The main loop
try:
    while True:
        proximity = sensors.get_proximity()

        # If the proximity crosses the threshold, toggle the mode
        if proximity > 1500 and time.time() - last_page > delay:
            mode += 1
            mode %= len(variables)
            last_page = time.time()

        # One mode for each variable
        if mode == 0:
            # variable = "temperature"
            unit = "C"
            data = sensors.get_adjusted_temperature(config.factor)
            display_text(variables[mode], data, unit)

        if mode == 1:
            # variable = "pressure"
            unit = "hPa"
            data = sensors.get_pressure()
            display_text(variables[mode], data, unit)

        if mode == 2:
            # variable = "humidity"
            unit = "%"
            data = sensors.get_humidity()
            display_text(variables[mode], data, unit)

        if mode == 3:
            # variable = "light"
            unit = "Lux"
            data =sensors.get_light()
            display_text(variables[mode], data, unit)

        if mode == 4:
            # variable = "oxidised"
            unit = "kO"
            data = sensors.get_oxidising
            display_text(variables[mode], data, unit)

        if mode == 5:
            # variable = "reduced"
            unit = "kO"
            data = sensors.get_reducing()
            display_text(variables[mode], data, unit)

        if mode == 6:
            # variable = "nh3"
            unit = "kO"
            data = sensors.get_nh3()
            display_text(variables[mode], data, unit)

# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
