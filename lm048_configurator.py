#!/usr/bin/env python

# lm048_configurator.py -- Script for configuring LM048 Bluetooth Serial Modules
#
# Copyright (C) 2016 Mitchell Gayner 
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.
#

import sys
import time
import serial
import serial.tools.list_ports

HANDSHAKE = "\xAA\xAA\xAA\xAA\xAA\xAA\xAA\xAA\x0D"
HANDSHAKE_ACK = "\xBB\xAA"

BAUD_RATE = {
    "BAUD14" : 19200, # default
    "BAUD10" : 1200,
    "BAUD11" : 2400,
    "BAUD12" : 4800,
    "BAUD13" : 9600,
    "BAUD15" : 38400,
    "BAUD16" : 57600,
    "BAUD17" : 115200,
    "BAUD18" : 230400,
    "BAUD19" : 460800,
    "BAUD20" : 921600,
}

PARITY = {
    "PAR0" : serial.PARITY_NONE,
    "PAR1" : serial.PARITY_ODD,
    "PAR2" : serial.PARITY_EVEN,
}

STOP_BITS = {
    "STOP1" : serial.STOPBITS_ONE,
    "STOP2" : serial.STOPBITS_TWO,
}

FLOW_CONTROL = {
    "FLOW-" : False,
    "FLOW+" : True,
}


def connect_to_device(portname):
    
    ser = serial.Serial()
    ser.baudrate = 921600
    ser.timeout = 5
    ser.port = portname

    ser.open()

    if handshake(ser):
        print "Connected to device -", get_device_name(ser)
        return ser

def handshake(serialport):
    time.sleep(2.0)
    serialport.write(HANDSHAKE)
    if HANDSHAKE_ACK == serialport.read(2):
        return ping_device(serialport)

    return False

def send_command(serialport, commandstr, replylines=1):
    serialport.reset_input_buffer()
    serialport.write(commandstr)
    serialport.readline()

    response = ""
    for i in range(0, replylines):
        response += serialport.readline()

    serialport.readline()
    return response.strip()

def ping_device(serialport):
    response = send_command(serialport, "AT\r")
    if response == "OK":
        return True
    return False

def get_device_name(serialport):
    return send_command(serialport, "AT+NAME?\r")

def read_baud_rate(serialport):
    response = send_command(serialport, "AT+BAUD?\r")
    return BAUD_RATE[response]

def set_baud_rate(serialport, baudrate):
    for key, value in BAUD_RATE.iteritems():
        if value == baudrate:
            return send_command(serialport, "AT+" + key + "\r")
    
    print "Unsupported baud rate"

def read_parity(serialport):
    response = send_command(serialport, "AT+PAR?\r")
    return PARITY[response]

def set_parity(serialport, parity):
    for key, value in PARITY.iteritems():
        if value == parity:
            return send_command(serialport, "AT+" + key + "\r")
    
    print "Unsupported parity"

def read_stop_bits(serialport):
    response = send_command(serialport, "AT+STOP?\r")
    return STOP_BITS[response]

def set_stop_bits(serialport, stopbits):
    for key, value in STOP_BITS.iteritems():
        if value == stopbits:
            return send_command(serialport, "AT+" + key + "\r")

def read_flow_control(serialport):
    response = send_command(serialport, "AT+FLOW?\r")
    return FLOW_CONTROL[response]

def set_flow_control(serialport, flowctrlmode):
    for key, value in FLOW_CONTROL.iteritems():
        if value == flowctrlmode:
            return send_command(serialport, "AT+" + key + "\r")
    
    print "Unsupported stop bits"

def return_to_data_mode(serialport):
    send_command(serialport, "AT+AUTO\r")

def baud_rate_format_human(bps):
    if bps > 115200:
        return str(bps / 1000.0) + "Kbps"

    return str(bps) + "bps"

print
print "Configure LM048 Bluetooth to Serial Adapters"
print 
print "List of Serial Ports"
print "--------------------"

ports = serial.tools.list_ports.comports()
for idx, val in enumerate(ports):
    print idx, "> ", val.device
print "q >  Quit"

while True:
    portnum = raw_input("Which port do you want to configure? > ")
    if portnum.lower() == "q":
        sys.exit(0)

    try:
        portnum = int(portnum)
        break
    except:
        continue

ser = connect_to_device(ports[portnum].device)

print "Serial settings Baud:", \
    baud_rate_format_human(read_baud_rate(ser)), \
    "Parity:", read_parity(ser), \
    "Stop bits:", read_stop_bits(ser), \
    "Flow control:", read_flow_control(ser)

setting_changed = False
while True:
    print "Choose setting"

    print "0 >  Baud rate"
    print "1 >  Parity"
    print "2 >  Stop bits"
    print "3 >  Flow control"
    print "q >  Quit"
    choice = raw_input(">").lower()

    if choice == "q":
        break
    elif choice == "0":
        setting = raw_input("Enter new baud rate >")
        set_baud_rate(ser, int(setting))

    elif choice == "1":
        setting = raw_input("Enter parity setting (n=None, o=Odd, e=Even) >").lower()
        if setting == "n":
            set_parity(ser, serial.PARITY_NONE)
        elif setting == "o":
            set_parity(ser, serial.PARITY_ODD)
        elif setting == "e":
            set_parity(ser, serial.PARITY_EVEN)

    elif choice == "2":
        setting = raw_input("Enter stop bits >").lower()
        if settings == "1":
            set_stop_bits(ser, serial.STOPBITS_ONE)
        elif settings == "2":
            set_stop_bits(ser, serial.STOPBITS_TWO)

    elif choice == "3":
        setting = raw_input("Enter flow control mode (0=Off, 1=On) >").lower()
        if setting == "0":
            set_flow_control(ser, False)
        elif setting == "1":
            set_flow_control(ser, True)

    if choice in ["0", "1", "2", "3"]:
        setting_changed = True

if setting_changed:
    print "New serial settings Baud:", \
        baud_rate_format_human(read_baud_rate(ser)), \
        "Parity:", read_parity(ser), \
        "Stop bits:", read_stop_bits(ser), \
        "Flow control:", read_flow_control(ser)

return_to_data_mode(ser)
ser.close()

