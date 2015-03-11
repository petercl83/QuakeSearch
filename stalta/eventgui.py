'''eventgui.py -- gui for programstalta.py

usage: python eventgui.py [options]

options:
    -h            print this
'''

version = "0.40"
lastchangedate = "2014-12-04"

import sys
import getopt
import os.path
import pprint

from Tkinter import *
import tkFont
import tkFileDialog
import tkMessageBox
# from ttk import *

import base
from logger import log
from programstalta import main as pgmmain
from programstalta import version as pgmversion


class App(Frame):

    def __init__(self, master):

        Frame.__init__(self, master)

        self.master = master
        self.truedatafile = ""
        self.statefile = ""
        self.isrunning = False

        self.entf = tkFont.Font(size = 12)
        self.lblf = tkFont.Font(size = 14)
        self.btnf = tkFont.Font(size = 16)

        # self.option_add("*background", "wheat")
        self.option_add("*Label*font", self.entf)
        self.option_add("*Entry*font", self.entf)
        self.option_add("*Button*font", self.btnf)

        row = 0
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)
        row += 1
        Label(master, text = "processing parameters", font = self.lblf,
              relief = RAISED, width = 30,
              ).grid(row = row, column = 3, columnspan = 2, sticky = W)
        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)


        row += 1
        Label(master, text = "Tsta").grid(row = row, column = 3, sticky = E)
        self.Tsta = StringVar()
        self.Tsta.set("0.25")
        Entry(master, width = 10, textvariable = self.Tsta
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "short time average window"
              ).grid(row = row, column = 5, sticky = W)
        Label(master, text = "seconds").grid(row = row, column = 6, sticky = W)

        row += 1
        Label(master, text = "Tlta").grid(row = row, column = 3, sticky = E)
        self.Tlta = StringVar()
        self.Tlta.set("90.0")
        Entry(master, width = 10, textvariable = self.Tlta
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "long time average window"
              ).grid(row = row, column = 5, sticky = W)
        Label(master, text = "seconds").grid(row = row, column = 6, sticky = W)

        row += 1
        Label(master, text = "Trigger").grid(row = row, column = 3, sticky = E)
        self.Triggerthreshold = StringVar()
        self.Triggerthreshold.set("4.0")
        Entry(master, width = 10, textvariable = self.Triggerthreshold
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "sta/lta trigger"
              ).grid(row = row, column = 5, sticky = W)
        Label(master, text = "ratio").grid(row = row, column = 6, sticky = W)

        row += 1
        Label(master, text = "Detrigger").grid(row = row,
                                               column = 3, sticky = E)
        self.Detriggerthreshold = StringVar()
        self.Detriggerthreshold.set("2.0")
        Entry(master, width = 10, textvariable = self.Detriggerthreshold
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "sta/lta de-trigger"
              ).grid(row = row, column = 5, sticky = W)
        Label(master, text = "ratio").grid(row = row, column = 6, sticky = W)

        row += 1
        Label(master, text = "Trigduration"
              ).grid(row = row, column = 3, sticky = E)
        self.Trigduration = StringVar()
        self.Trigduration.set("30.0")
        Entry(master, width = 10, textvariable = self.Trigduration,
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "minimum event duration"
              ).grid(row = row, column = 5, sticky = W)
        Label(master, text = "secs").grid(row = row, column = 6, sticky = W)

        row += 1
        Label(master, text = "Trigdesense"
              ).grid(row = row, column = 3, sticky = E)
        self.Trigdsensetime = StringVar()
        self.Trigdsensetime.set("1000.0")
        Entry(master, width = 10, textvariable = self.Trigdsensetime,
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "lta desense time"
              ).grid(row = row, column = 5, sticky = W)
        Label(master, text = "secs").grid(row = row, column = 6, sticky = W)

        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)

        row += 1
        Label(master, text = "logging parameters", font = self.lblf,
              relief = RAISED, width = 30,
              ).grid(row = row, column = 3, columnspan = 2, sticky = W)
        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)

        row += 1
        Label(master, text = "Loglevel"
              ).grid(row = row, column = 3, sticky = E)
        self.llboxv = StringVar()
        self.llb = Spinbox(master, textvariable = self.llboxv,
                           values = ("debug", "info", "warning"))
        self.llb.grid(row = row, column = 4, sticky = W)
        Label(master, text = "logging level"
              ).grid(row = row, column = 5, sticky = W)


        row += 1
        Label(master, text = "Shortlogfile"
              ).grid(row = row, column = 3, sticky = E)
        self.Logfile = StringVar()
        self.Logfile.set("")
        Entry(master, width = 10, textvariable = self.Logfile
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "regular log filename"
              ).grid(row = row, column = 5, sticky = W)

        row += 1
        Label(master, text = "Longlogfile"
              ).grid(row = row, column = 3, sticky = E)
        self.LongLogfile = StringVar()
        self.LongLogfile.set("")
        Entry(master, width = 10, textvariable = self.LongLogfile
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "cumulative log filename"
              ).grid(row = row, column = 5, sticky = W)

        row += 1
        Label(master, text = "Outfile"
              ).grid(row = row, column = 3, sticky = E)
        self.Outfile = StringVar()
        self.Outfile.set("")
        self.Outshowfile = StringVar()
        self.Outshowfile.set("")
        Entry(master, width = 10, textvariable = self.Outshowfile
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "output sac filename"
              ).grid(row = row, column = 5, sticky = W)
        Button(master, text = "browse...", command = self.OnOutBrowse,
               font = self.lblf,
               ).grid(row = row, column = 6, sticky = W)

        row += 1
        Label(master, text = "Eventfile"
              ).grid(row = row, column = 3, sticky = E)
        self.Eventfile = StringVar()
        self.Eventfile.set("")
        Entry(master, width = 10, textvariable = self.Eventfile
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "event spreadsheet filename"
              ).grid(row = row, column = 5, sticky = W)

        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)

        row += 1
        Label(master, text = "control parameters", font = self.lblf,
              relief = RAISED, width = 30,
              ).grid(row = row, column = 3, columnspan = 2, sticky = W)
        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)

        row += 1
        Label(master, text = "Jobduration"
              ).grid(row = row, column = 3, sticky = E)
        self.Jobduration = StringVar()
        self.Jobduration.set("")
        Entry(master, width = 10, textvariable = self.Jobduration
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "length of acquisition"
              ).grid(row = row, column = 5, sticky = W)
        Label(master, text = "secs").grid(row = row, column = 6, sticky = W)

        row += 1
        self.Doalarm = IntVar()
        Checkbutton(master, text = "event alarm", variable = self.Doalarm,
                    font = self.entf,
                    ).grid(row = row, column = 3, sticky = E)
        self.Alarmduration = StringVar()
        self.Alarmduration.set("30.0")
        Entry(master, width = 10, textvariable = self.Alarmduration
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "duration of alarm"
              ).grid(row = row, column = 5, sticky = W)
        Label(master, text = "secs").grid(row = row, column = 6, sticky = W)

        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)

        row += 1
        Label(master, text = "data source", font = self.lblf,
              relief = RAISED, width = 30,
              ).grid(row = row, column = 3, columnspan = 2, sticky = W)
        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)


        row += 1
        self.Comcheck = IntVar()
        Checkbutton(master, text = "use comport", variable = self.Comcheck,
                    font = self.entf,
                    ).grid(row = row, column = 3, sticky = E)
        self.comport = StringVar()
        self.comport.set("com7")
        Entry(master, width = 10, textvariable = self.comport
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "active comport"
              ).grid(row = row, column = 5, sticky = W)

        row += 1
        self.datafile = StringVar()
        self.datafile.set("")
        self.truedatafile = StringVar()
        self.truedatafile.set("")
        Entry(master, textvariable = self.datafile,
              ).grid(row = row, column = 4, sticky = W)
        Label(master, text = "existing data file"
              ).grid(row = row, column = 5, sticky = W)
        Button(master, text = "browse...", command = self.OnBrowse,
               font = self.lblf,
               ).grid(row = row, column = 6, sticky = W)


        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)

        row += 1
        Label(master, text = "display control", font = self.lblf,
              relief = RAISED, width = 30,
              ).grid(row = row, column = 3, columnspan = 2, sticky = W)
        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)


        row += 1
        self.doplot = IntVar()
        Checkbutton(master, text = "plot results", variable = self.doplot,
                    font = self.entf,
                    ).grid(row = row, column = 4, columnspan = 2, sticky = W)

        row += 1
        self.doplotavg = IntVar()
        Checkbutton(master, text = "also plot running averages",
                    variable = self.doplotavg,
                    font = self.entf,
                    ).grid(row = row, column = 4, columnspan = 2, sticky = W)

        row += 1
        self.showcommand = IntVar()
        Checkbutton(master, text = "show command line",
                    variable = self.showcommand,
                    font = self.entf,
                    ).grid(row = row, column = 4, columnspan = 2, sticky = W)

        row += 1
        Label(master, text = "  ").grid(row = row, column = 3, sticky = W)

        row += 1
        col = 3
        Button(master, fg = "blue", text = "run",
               command = self.OnRun).grid(row = row, column = col, sticky = N)
        col += 1
        Button(master, fg = "magenta", text = "finish",
               command = self.OnFinish).grid(row = row, column = col, sticky = N)
        col += 1
        Button(master, fg = "blue", text = "save",
               command = self.saveState).grid(row = row, column = col, sticky = N)
        col += 1
        Button(master, fg = "blue", text = "load",
               command = self.loadState).grid(row = row, column = col, sticky = N)
        col += 1
        Button(master, fg = "red", text = "quit",
               command = self.OnQuit).grid(row = row, column = col, sticky = N)
        col += 1
        Label(master, fg = "red", text = "      ",
              ).grid(row = row, column = col, sticky = W)


    def OnRun(self):
        args = [
            "eventgui",
            "-g",
            "-S", self.Tsta.get(),
            "-L", self.Tlta.get(),
            "-T", self.Triggerthreshold.get(),
            "-D", self.Detriggerthreshold.get(),
            "-P", self.Trigduration.get(),
            "-F", self.Trigdsensetime.get(),
            "-l", self.llboxv.get(),
        ]
        if self.Logfile.get() != "":
            args.extend(("-w", self.Logfile.get()))
        if self.LongLogfile.get() != "":
            args.extend(("-a", self.LongLogfile.get()))
        if self.Outfile.get() != "":
            args.extend(("-s", self.Outfile.get()))
        elif self.Outshowfile.get() != "":
            args.extend(("-s", self.Outshowfile.get()))
        if self.Eventfile.get() != "":
            args.extend(("-e", self.Eventfile.get()))
        if self.doplot.get() != 0:
            args.append("-p")
            if self.doplotavg.get() != 0:
                args.append("-r")
        if self.Doalarm.get():
            pass
        else:
            args.append("-q")
        if self.Comcheck.get() == 0:
            args.append("-q")
            if self.truedatafile.get() != "":
                args.append("-m")
                args.append(self.truedatafile.get())
            elif self.datafile.get() != "":
                args.append("-m")
                args.append(self.datafile.get())
            else:
                tkMessageBox.showerror(title = "inconsistent request",
                    message = "check 'use comport' or provide a data file")
                return
        else:
            args.extend(("-c", self.comport.get()))
            if self.Jobduration.get() != "":
                args.extend(("-i", self.Jobduration.get()))
        if self.showcommand.get():
            print >> sys.stderr, "--------command line-----------"
            pprint.pprint(args, stream = sys.stderr)
            print >> sys.stderr, "-------------------------------"
        base.Globs["quitflag"] = False
        base.Globs["finishflag"] = False
        self.isrunning = True
        r = pgmmain(args)
        self.isrunning = False
        if r != 0:
            log().error("pgmmain returned %s" % r)
            self.reallyquit()
        if base.Globs["quitflag"]:
            self.reallyquit()
        base.Globs["quitflag"] = True
        base.Globs["finishflag"] = True

    def OnOutBrowse(self):
        self.Outfile.set(tkFileDialog.asksaveasfilename(
            filetypes = [('sac data file', '*.sac')]))
        if self.Outfile.get() != "":
            self.Outshowfile.set(os.path.basename(self.Outfile.get()))


    def OnBrowse(self):
        self.truedatafile.set(tkFileDialog.askopenfilename())
        if self.truedatafile.get() != "":
            self.datafile.set(os.path.basename(self.truedatafile.get()))


    def loadState(self):
        pass


    def saveState(self):
        pass


    def reallyquit(self):
        self.quit()


    def OnFinish(self):
        base.Globs["finishflag"] = True


    def OnQuit(self):
        if not self.isrunning:
            self.reallyquit()
        if base.Globs["quitflag"]:
            self.reallyquit()
        base.Globs["quitflag"] = True



def main(argv=None):
    if argv is None:
        argv = sys.argv

    options = "h"

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

        root = Tk()
        app = App(root)

        base.Globs["predatacallback"] = app.update
        compositeversion = "%.2f" % (float(version) + float(pgmversion))
        app.master.title("sta/lta event detection"
                         + "           version " + compositeversion
                         + "              "
                         + "   [gui " + version
                         + "   algorithm " + pgmversion + "]")
        app.mainloop()
        try:
            root.destroy()
        except:
            pass

    except Exception, e:
        log().exception("gui error")
        print >> sys.stderr, e
        return 3


if __name__ == "__main__":
    sys.exit(main())
