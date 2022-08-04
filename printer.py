#!/usr/bin/python

import usb.core
import usb.util
import serial
import socket

from escpos import *
from constants import *
from exceptions import *

class Usb(Escpos):
    """ Define USB printer """

    def __init__(self, seri, idVendor, idProduct, interface=0, in_ep=0x82, out_ep=0x01):
        """
        @param seri     : Device Series
        @param idVendor  : Vendor ID
        @param idProduct : Product ID
        @param interface : USB device interface
        @param in_ep     : Input end point
        @param out_ep    : Output end point
        """
        self.seri      = seri
        self.idVendor  = idVendor
        self.idProduct = idProduct
        self.interface = interface
        self.in_ep     = in_ep
        self.out_ep    = out_ep
        self.open()


    def open(self):
        """ Search device on USB tree and set is as escpos device """
        self.device = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)
        if self.device is None:
            print "Cable isn't plugged in"

        check_driver = None

        try:
            check_driver = self.device.is_kernel_driver_active(0)
        except NotImplementedError:
            pass

        if check_driver is None or check_driver:
            try:
                self.device.detach_kernel_driver(0)
            except usb.core.USBError as e:
                if check_driver is not None:
                    print "Could not detatch kernel driver: %s" % str(e)

        try:
            self.device.set_configuration()
            self.device.reset()
        except usb.core.USBError as e:
            print "Could not set configuration: %s" % str(e)


    def _raw(self, msg):
        """ Print any command sent in raw format """
        self.device.write(self.out_ep, msg, self.interface)

    def raw_(self):
        """ Read Printer in raw format """
        rslt=self.device.read(self.in_ep, 16,0)
        return rslt

    def __del__(self):
        """ Release USB interface """
        if self.device:
            usb.util.dispose_resources(self.device)
        self.device = None



class Serial(Escpos):
    """ Define Serial printer """

    def __init__(self, seri="EPSON",devfile="/dev/ttyS0", baudrate=9600, bytesize=8, timeout=0.3,
                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                 xonxoff=False , dsrdtr=True):
        """
        @param seri     : Device Series
        @param devfile  : Device file under dev filesystem
        @param baudrate : Baud rate for serial transmission
        @param bytesize : Serial buffer size
        @param timeout  : Read/Write timeout
        
        @param parity   : Parity checking
        @param stopbits : Number of stop bits
        @param xonxoff  : Software flow control
        @param dsrdtr   : Hardware flow control (False to enable RTS/CTS)
        """
        self.seri     = seri
        self.devfile  = devfile
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.timeout  = timeout
        
        self.parity = parity
        self.stopbits = stopbits
        self.xonxoff = xonxoff
        self.dsrdtr = dsrdtr
        
        self.open()


    def open(self):
        """ Setup serial port and set is as escpos device """
        self.device = serial.Serial(port=self.devfile, baudrate=self.baudrate,
                                    bytesize=self.bytesize, parity=self.parity,
                                    stopbits=self.stopbits, timeout=self.timeout,
                                    xonxoff=self.xonxoff, dsrdtr=self.dsrdtr)

        if self.device is not None:
            print "Serial printer enabled"
        else:
            print "Unable to open serial printer on: %s" % self.devfile


    def _raw(self, msg):
        """ Print any command sent in raw format """
        self.device.write(msg)

    def raw_(self):
        """ Read Printer in raw format """
        rslt_ = self.device.readline()
        _rslt = rslt_.encode('hex') 
        x     = 0
        rslt  = []
        for _rslt_ in _rslt[::2]:
            #'{:x}'.format(int(hex(_double),0)).zfill(2)
            rslt.append(int(_rslt[x:x+2],16))
            x=x+2
        return rslt


    def __del__(self):
        """ Close Serial interface """
        if self.device is not None:
            self.device.close()



class Network(Escpos):
    """ Define Network printer """

    def __init__(self,seri,host,port=9100):
        """
        @param seri     : Device Series
        @param host : Printer's hostname or IP address
        @param port : Port to write to
        """
        self.seri = seri
        self.host = host
        self.port = port
        self.open()


    def open(self):
        """ Open TCP socket and set it as escpos device """
        self.device = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.device.connect((self.host, self.port))

        if self.device is None:
            print "Could not open socket for %s" % self.host


    def _raw(self, msg):
        """ Print any command sent in raw format """
        self.device.send(msg)


    def __del__(self):
        """ Close TCP connection """
        self.device.close()



class File(Escpos):
    """ Define Generic file printer """

    def __init__(self, seri, devfile="/dev/usb/lp0"):
        """
        @param seri     : Device Series
        @param devfile : Device file under dev filesystem
        """
        self.seri    = seri
        self.devfile = devfile
        self.open()


    def open(self):
        """ Open system file """
        self.device = open(self.devfile, "wb")

        if self.device is None:
            print "Could not open the specified file %s" % self.devfile

    def flush(self):
        """ Flush printing content """
        self.device.flush()

    def _raw(self, msg):
        """ Print any command sent in raw format """
        self.device.write(msg);
        self.flush()

    def raw_(self):
        """ Print any command sent in raw format """
        #self.device.write(msg);        
        #rslt=self.device.read()
        return 

    def __del__(self):
        """ Close system file """
        self.device.flush()
        self.device.close()
