'''base.py -- base module for global items'''

import Queue

BaseQ = Queue.Queue()

SerinQ = Queue.Queue()


def __dummyfcn():
    return


Globs = {
    "loginit": False,
    "predatacallback": __dummyfcn,
    "postdatacallback": __dummyfcn,
    "quitflag": False,
    "finishflag": False,
}








