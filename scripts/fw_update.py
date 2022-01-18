#!/usr/bin/env python3
"""
ODrive command line utility
"""

from __future__ import print_function
import sys

# We require Python 3.5 for the "async def" syntax.
if sys.version_info <= (3, 5):
    print("Your Python version (Python {}.{}) is too old. Please install Python 3.5 or newer.".format(
        sys.version_info.major, sys.version_info.minor
    ))
    exit(1)

import sys
import os
import argparse
import time
import math

import odrive
from odrive.utils import OperationAbortedException
from odrive.configuration import *
from fibre import Logger, Event

# Flush stdout by default
# Source:
# https://stackoverflow.com/questions/230751/how-to-flush-output-of-python-print
old_print = print
def print(*args, **kwargs):
    kwargs.pop('flush', False)
    old_print(*args, **kwargs)
    file = kwargs.get('file', sys.stdout)
    file.flush() if file is not None else sys.stdout.flush()

script_path=os.path.dirname(os.path.realpath(__file__))

## Parse arguments ##
parser = argparse.ArgumentParser(description='ODrive command line utility\n'
                                             'Running this tool without any arguments is equivalent to running `odrivetool shell`\n',
                                 formatter_class=argparse.RawTextHelpFormatter)

# General arguments
parser.add_argument("-f", "--file", metavar='HEX', action="store",
                        help='The .hex file to be flashed. Make sure target board version '
                        'of the firmware file matches the actual board version. '
                        'You can download the latest release manually from '
                        'https://github.com/madcowswe/ODrive/releases. '
                        'If no file is provided, the script automatically downloads '
                        'the latest firmware.')

parser.add_argument("-p", "--path", metavar="PATH", action="store",
                    help="The path(s) where ODrive(s) should be discovered.\n"
                    "By default the script will connect to any ODrive on USB.\n\n"
                    "To select a specific USB device:\n"
                    "  --path usb:BUS:DEVICE\n"
                    "usbwhere BUS and DEVICE are the bus and device numbers as shown in `lsusb`.\n\n"
                    "To select a specific serial port:\n"
                    "  --path serial:PATH\n"
                    "where PATH is the path of the serial port. For example \"/dev/ttyUSB0\".\n"
                    "You can use `ls /dev/tty*` to find the correct port.\n\n"
                    "You can combine USB and serial specs by separating them with a comma (no space!)\n"
                    "Example:\n"
                    "  --path usb,serial:/dev/ttyUSB0\n"
                    "means \"discover any USB device or a serial device on /dev/ttyUSB0\"")
parser.add_argument("-s", "--serial-number", action="store",
                    help="The 12-digit serial number of the device. "
                         "This is a string consisting of 12 upper case hexadecimal "
                         "digits as displayed in lsusb. \n"
                         "    example: 385F324D3037\n"
                         "You can list all devices connected to USB by running\n"
                         "(lsusb -d 1209:0d32 -v; lsusb -d 0483:df11 -v) | grep iSerial\n"
                         "If omitted, any device is accepted.")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="print debug information")
parser.add_argument("--version", action="store_true",
                    help="print version information and exit")

parser.set_defaults(path="usb:idVendor=0x1209,idProduct=0x0D32,bInterfaceClass=0,bInterfaceSubClass=1,bInterfaceProtocol=0")
args = parser.parse_args()
logger = Logger(verbose=args.verbose)

def print_version():
    sys.stderr.write("ODrive control utility v" + odrive.__version__ + "\n")
    sys.stderr.flush()

app_shutdown_token = Event()

try:
  import odrive.dfu
  odrive.dfu.launch_dfu(args, logger, app_shutdown_token)

except OperationAbortedException:
    logger.info("Operation aborted.")

finally:
    app_shutdown_token.set()
