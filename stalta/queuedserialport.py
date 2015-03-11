'''serial port in a separate thread feeding a Queue'''

import time
import threading
import serial

from logger import log
import base


class ThreadedSerialPort(threading.Thread):
    def __init__(self,
                 ttynameorfile,
                 baudrate = 9600,
                 timeout = 1.0,
                 ):
        threading.Thread.__init__(self)
        log().debug("initializing ThreadedSerialPort")
        self.ttynameorfile = ttynameorfile
        self.baudrate = baudrate
        self.timeout = timeout
        try:
            self.tty = serial.Serial(port = self.ttynameorfile,
                                     timeout = self.timeout,
                                     baudrate = self.baudrate,
                                     bytesize = serial.EIGHTBITS,
                                     parity = serial.PARITY_NONE,
                                     stopbits = serial.STOPBITS_ONE,
                                     )
        except:
            log().exception("serial port open failure")
            base.Globs["quitflag"] = True
            raise
        self.setDaemon(1)
        self.start()


    def run(self):
        log().debug("serial processor infinite loop begin")
        qrange = 0
        nin = 0
        while True:
            if base.Globs["finishflag"] or base.Globs["quitflag"]:
                self.tty.close()
                return
            try:
                l = self.tty.readline().strip()
                vtime = time.time()
                nin += 1
                if nin <= 10:  # skip first ten values
                    continue
            except:
                log().exception("serial port readline failed")
                base.Globs["quitflag"] = True
                return 1
            base.SerinQ.put((l, vtime))
            qsize = base.SerinQ.qsize()
            cqrange = int(qsize / 10.0)
            if cqrange != qrange:
                log().warning("SerinQ size %d" % qsize)
            qrange = cqrange
            time.sleep(0.001)
