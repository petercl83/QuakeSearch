'''programstalta.py: sta/lta event detection on a serial data stream

usage: python programstalta.py [options] [datafiles]

options:
    -h             print this
    -v             be more verbose
    -g             called from gui
    -c comport     serial port [com7]
    -s filename    write data stream to a sac file
    -w filename    log to a new file named filename
    -a filename    append log to (possibly pre-existing) filename
    -e filename    write event spreadsheet to filename
    -d             use default log file names
    -i duration    acquire data for duration seconds and then finish
    -l level       log level [info] of (error, warn, info, debug)
    -m             instantiate Queue logger
    -p             plot results using matplotlib
    -r             show running averages on the plot
    -q             don't make alarm sounds
    -S tsta        set Tsta
    -L tlta        set Tlta
    -T tthresh     set Triggerthreshold
    -D dtthresh    set Detriggerthreshold
    -F tdesense    set Trigdsensetime
    -P trigdur     set Triggerduration
    -A alarmdur    set Alarmduration

If one or more of the optional arguments, shown as datafiles above,
are present, each argument must be the name of amaseis data file, a
sac data file, a columnar data file, or a wav data file.  Each of
these files is processed by the program as though it were the input
data stream.  Each is handled separately and the apparent output times
(but not the time in the log header) are adjusted to make the sta/lta
algorithm work properly.  When one or more file arguments are present,
the program does not open the serial port.'''

version = "2.50"
lastchangedate = "2014-12-04"

import sys
import getopt
import time
import datetime
import math
import os.path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

import base
from logger import *
import datainput
import dataoutput
import scanevents
import queuedserialport


try:
    import winsound
    has_winsound = True
except:
    has_winsound = False



# default configuration variables

Soundfile = "c:/Windows/Media/Alarms/divehorn.wav"
Comport = "com7"
Samplespersecond = 18.78
Zzero = 32768
Tsta = 0.25
Tlta = 90.0
Triggerthreshold = 5.0
Detriggerthreshold = 2.0
Trigdsensetime = 100.0
Trigduration = 30.0
Alarmduration = 30.0

# import everything from the configstalta module
#
# from configstalta import *
#


def alarmfcn(a = None, b = None, c = None):
    if has_winsound:
        winsound.PlaySound(a, b)
    else:
        pass



def do_plot(tin, y, sta, lta, ratio, trigs,
            dt, t0, tsta, tlta, trig, detrig, desense,
            filenamebase,
            plotavgs = True, isgui = False):

    y = np.array(y)
    dtime = [datetime.datetime.utcfromtimestamp(x) for x in tin]
    dtmin = dtime[0]
    dtmax = dtime[-1]

    yabs = np.abs(y)
    ymax = max(yabs)

    sta = np.array(sta)
    lta = np.array(lta)
    ratio = np.array(ratio)
    pmax = max(sta.max(), lta.max())
    rmax = max(ratio.max(), trig, detrig)

    plt.figure()
    plt.title(("%s   %d events" + "\n"
        + "Tsta: %.3g  Tlta: %.3g  Trig: %.3g  Detrig: %.2g  Tdsense: %.3g")
        % (filenamebase, len(trigs), tsta, tlta, trig, detrig, desense))
    plt.ylabel("ratio")

    plt.plot(dtime, yabs / ymax, color = "0.4", label = "_ignore")
    if plotavgs:
        plt.plot(dtime, rmax*lta/pmax, color = "orange", label = "lta")
        plt.plot(dtime, rmax*sta/pmax, color = "green", label = "sta")
    plt.plot(dtime, ratio, color = "red", label = "ratio")
    plt.plot((dtmin, dtmax), (trig, trig), "k--")
    plt.plot((dtmin, dtmax), (detrig, detrig), "k--")
    plt.legend()
    for tl, tr, retrigs in trigs:
        tl, tr = [datetime.datetime.utcfromtimestamp(x) for x in (tl, tr)]
        xpoly = (tl, tr, tr, tl)
        ypoly = (rmax, rmax, detrig, detrig)
        plt.fill(xpoly, ypoly, color = "0.7")

    fmtr = mpl.dates.DateFormatter("%H:%M:%S")
    plt.gca().xaxis.set_major_formatter(fmtr)
    plt.gcf().autofmt_xdate()
    plt.show(block = False if isgui else True)



def ctime2str(ctime):
    "float time to usable, short string"
    secs, fracs = divmod(ctime, 1.0)
    stt = time.gmtime(ctime)
    strt = "%02d:%02d:%02d.%02d" % (stt.tm_hour, stt.tm_min, stt.tm_sec,
                                    int(100 * fracs))
    return strt



class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv = None):
    if argv is None:
        argv = sys.argv

    global Tsta, Tlta, Triggerthreshold, Detriggerthreshold
    global Trigdsensetime, Trigduration
    global Alarmduration

    options = "vhgw:a:e:dc:s:i:l:mprqS:L:D:T:A:F:P:" # : indicates something after key

    logfiles = []
    loglevel = "info"
    comport = Comport
    verbose = 1
    doQueue = False
    doPlot = False
    doPlotavgs = False
    evfile = None
    sacfile = None
    job_duration = None
    isgui = False

    setLogTime(time.gmtime)
    doalarm = True

    try:
        try:
            opts, datafiles = getopt.getopt(argv[1:], options, ["help"])
        except getopt.error, msg:
            raise Usage(msg)

        # process options
        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__ + "\n\n" + version
                sys.exit(0)
            elif o == "-v":
                verbose += 1
            elif o == "-g": #GUI
                isgui = True
            elif o == "-w": #log to new filename, default logfiles=[]
                logfiles.append((a, "wb")) 
            elif o == "-a": #append to filename
                logfiles.append((a, "ab"))
            elif o == "-e": #write event spreadsheet to filename
                evfile = a
            elif o == "-d":
                logfiles = []
                logfiles.append(("longlog.txt", "ab"))
                logfiles.append(("shortlog.txt", "wb"))
            elif o == "-l": #loglevel [info] of (error, warn, info, debug)
                loglevel = a 
            elif o == "-c": 
                comport = a 
            elif o == "-s":
                sacfile = a
            elif o == "-i": #default job_duratioln = None
                job_duration = float(a)
            elif o == "-m": #instantiate Queue logger
                doQueue = True
            elif o == "-p": #Plot
                doPlot = True
            elif o == "-r": #show running averages
                doPlotavgs = True
            elif o == "-q": #don't do alarm
                doalarm = False
            elif o == "-S":
                Tsta = float(a)
            elif o == "-L":
                Tlta = float(a)
            elif o == "-T":
                Triggerthreshold = float(a)
            elif o == "-D":
                Detriggerthreshold = float(a)
            elif o == "-F":
                Trigdsensetime = float(a)
            elif o == "-P":
                Trigduration = float(a)
            elif o == "-A":
                Alarmduration = float(a)

        configureStream(loglevel, sys.stderr)
        if doQueue:
            configureQueue(loglevel, base.BaseQ)
        for fname, fmode in logfiles:
            configureFile(loglevel, fname, fmode)

        datafiles = list(datafiles)
        if len(datafiles) > 0:
            datain = None
            iomode = "virtual"
        else:
            iomode = "real"
            try:
                datain = queuedserialport.ThreadedSerialPort(
                    comport,
                    baudrate = 9600,
                    timeout = 1.0,
                )
                fbase = comport
            except:
                log().exception("serial port error")
                print >> sys.stderr, \
                    "fatal error: serial open failed for %s" % comport
                sys.exit(0)

        sps = Samplespersecond
        dt = 1.0 / sps

        # computed quantities

        Nsta = max(5, int(math.ceil(Tsta * sps)))
        Nlta = max(Nsta + 5, int(math.ceil(Tlta * sps)))

        # lists to store the windowed data

        Zsta = Nsta * [0.0]
        Zlta = Nlta * [0.0]

        # initialize stuff

        log().critical("start programstalta.py: sta/lta event detection")
        log().critical("version " + version)
        log().info("iomode = %s" % iomode)
        log().info("  Nsta: %d  Nlta: %d" % (Nsta, Nlta))
        if len(datafiles) > 0:
            log().debug("datafiles: %s" % str(datafiles))

        nin = 0
        fninlta = 0.0
        ntrig = 0
        state = "detriggered"
        alarmstate = None
        dataary = []  # need an initial zero-length array
        tary = []
        yary = []
        rary = []
        sary = []
        lary = []
        trigs = []

        starttime = time.time()
        job_starttime = time.time()
        t0 = starttime
        totaltrigtime = 0.0

        while True:

            base.Globs["predatacallback"]()
            if base.Globs["quitflag"]:
                return 0

            finishflag = base.Globs["finishflag"]
            if job_duration is not None:
                job_done = (time.time() - job_starttime) >= job_duration
            else:
                job_done = False
            data_done = (iomode == "virtual"
                    and len(dataary) > 0 and nin >= len(dataary))
            if finishflag or job_done or data_done:
                fractrigtime = float(totaltrigtime) \
                               / max(1.0, vtime - starttime)
                log().info("last sample time: %s" % ctime2str(vtime))
                log().info("total:  samples %d   time %.5g sec"
                           % (nin, vtime - starttime))
                log().info("total event time:  %.3g sec (%.2g%%)"
                           % (totaltrigtime, 100.0 * fractrigtime))
                if sacfile is not None:
                    log().info("sac to %s" % sacfile)
                    dataoutput.writesac(sacfile, tary, yary, starttime)
                if evfile is not None and doQueue:
                    log().info("events to %s" % evfile)
                    scanevents.scanstream(base.BaseQ, evfile)
                if doPlot:
                    do_plot(tary, yary, sary, lary, rary, trigs,
                            dt, t0, Tsta, Tlta,
                            Triggerthreshold, Detriggerthreshold,
                            Trigdsensetime,
                            fbase, doPlotavgs, isgui)
                if base.Globs["finishflag"] or job_done:
                    return 0

            if iomode == "real":
                try:
                    xstr, vtime = base.SerinQ.get(True, 10.0)
                except:
                    log().exception("SerinQ error")
                    return 1
                if len(xstr) == 0:
                    continue
                y = float(xstr) - Zzero

            else:
                if nin >= len(dataary):
                    if len(datafiles) <= 0:  # no more files to process
                        return 0
                    # start the next (first) data file
                    currentfile = datafiles.pop(0)
                    fpath, fbase = os.path.split(currentfile)
                    log().info("file: '%s'" % fbase)
                    log().info("  path: '%s'" % fpath)
                    datain = datainput.FileScanner(currentfile)
                    dataary, dt, t0, info = datain['data'][0]
                    log().info("  starttime %s"
                               % time.asctime(time.gmtime(t0)))
                    log().info("  dt: %.3f  sps: %.2f  t0: %.1f"
                               % (dt, 1.0/dt, t0))
                    # recompute the arrays, etc
                    sps = 1.0 / dt
                    Nsta = max(5, int(math.ceil(Tsta * sps)))
                    Nlta = max(Nsta + 5, int(math.ceil(Tlta * sps)))
                    log().info("  Nsta: %d  Nlta: %d" % (Nsta, Nlta))
                    Zsta = Nsta * [0.0]
                    Zlta = Nlta * [0.0]
                    tary = []
                    yary = []
                    rary = []
                    sary = []
                    lary = []
                    trigs = []
                    nin = 0
                    fninlta = 0.0
                    starttime = t0
                    ntrig = 0
                    state = "detriggered"
                    alarmstate = None

                y = float(dataary[nin])
                vtime = nin * dt + t0

            if nin == 0:
                log().info("  Tsta: %.1f  Tlta: %.1f  Tthr: %.1f  Dthr: %.1f"
                           % (Tsta, Tlta, Triggerthreshold, Detriggerthreshold))
                log().info("  sps: %.3f  Fdesens: %.1f"
                           % (sps, Trigdsensetime, ))
                log().info("first sample time: %s" % ctime2str(vtime))

            # circular data buffers: all that matters is the sum.
            nin += 1
            fninlta += 1.0 if state == "detriggered" \
                       else (1.0 / max(1.0, Trigdsensetime * sps))
            Zsta[nin % Nsta] = abs(y)
            Zlta[int(fninlta) % Nlta] = abs(y)

            ysta = sum(Zsta) / float(Nsta)
            ylta = sum(Zlta) / float(Nlta)
            ratio = ysta / max(1.0 / Nlta, ylta)
            if nin < max(Nsta, Nlta):
                ratio = 1.0

            tary.append(vtime)
            yary.append(y)
            sary.append(ysta)
            lary.append(ylta)
            rary.append(ratio)

            if nin < max(Nlta, Nsta):  # skip tests until the Z arrays are full
                continue
            elif nin == max(Nlta, Nsta):
                log().info("begin ratio testing at sample %d" % nin)

            base.Globs["postdatacallback"]()
            if state == "detriggered":
                if ratio >= Triggerthreshold:
                    ntrig += 1
                    log().info("trigger[%d] at %s" % (ntrig, ctime2str(vtime)))
                    trigtime = vtime
                    lasttrigtime = vtime
                    retriggers = 0
                    if alarmstate is None and doalarm and iomode == "real":
                        winsound.PlaySound(Soundfile,
                                           winsound.SND_FILENAME
                                           | winsound.SND_LOOP
                                           | winsound.SND_ASYNC)
                    alarmstate = vtime + Alarmduration
                    state = "triggered"

            else:  # must be in triggered state
                trigtimeused = vtime >= (lasttrigtime + Trigduration)
                if ratio <= Detriggerthreshold and trigtimeused:
                    duration = vtime - trigtime
                    totaltrigtime += duration
                    fractrigtime = float(totaltrigtime) \
                                   / max(1.0, vtime - starttime)
                    log().info("    lasted %.3f sec   %d retriggers"
                               % (duration, retriggers))
                    log().info("    cumulative:  %.3g sec   %.3g%%"
                                   % (totaltrigtime, 100.0 * fractrigtime))
                    state = "detriggered"
                    trigs.append((trigtime, vtime, retriggers))
                elif ratio >= Triggerthreshold:
                    lasttrigtime = vtime
                    retriggers += 1

            if alarmstate is not None:
                if (vtime >= alarmstate) or (state == "detriggered"):
                    if doalarm and iomode == "real":
                        winsound.PlaySound(None, winsound.SND_ASYNC)
                    alarmstate = None

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use -h"
        return 2

    except Exception, e:
        log().exception("run-time error")
        print >> sys.stderr, e
        return 3


if __name__ == "__main__":
    sys.exit(main())
