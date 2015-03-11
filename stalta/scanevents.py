'''scan a log stream and extract event info'''

import re
import xlsxwriter as xls


def scanstream(stream, filename):

    trigger_re = "^INFO (\S+) (\S+):\s+trigger\[(\d+)\] at (\S+)$"
    trigcre = re.compile(trigger_re)
    duration_re = "^INFO (\S+) (\S+):\s+lasted (\S+) seconds$"
    durcre = re.compile(duration_re)

    events = []
    state = "4event"
    try:
        while True:
            s = stream.get(False)
            if s is None:
                break
            s = s.strip()
            if len(s) == 0:
                continue
            if state == "4event":
                trig = re.match(trigcre, s)
                if trig is None:
                    continue
                rd, rt, trign, goodt = trig.groups()
                state = "4duration"
                # print goodt
            else:  # state == "4duration"
                dur = re.match(durcre, s)
                if dur is None:
                    continue
                xd, xt, tdur = dur.groups()
                events.append((rd, rt, trign, goodt, tdur))
                state = "4event"
                # print (rd, rt, trign, goodt, tdur)

    except:
        pass

    wb = xls.Workbook(filename)
    ws = wb.add_worksheet('events')

    bold = wb.add_format({'bold': True})
    ws.write('A1', 'date', bold)
    ws.write('B1', 'time', bold)
    ws.write('C1', 'event id', bold)
    ws.write('D1', 'event time', bold)
    ws.write('E1', 'duration', bold)

    r = 1
    for rd, rt, trign, goodt, tdur in events:
        c = 0
        ws.write(r, c, rd)
        c += 1
        ws.write(r, c, rt)
        c += 1
        ws.write(r, c, trign)
        c += 1
        ws.write(r, c, goodt)
        c += 1
        ws.write(r, c, tdur)
        r += 1

    wb.close()
