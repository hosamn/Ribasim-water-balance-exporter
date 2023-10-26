# -*- coding: utf-8 -*-
##############################################################
# HIS Reader Lib.
# by Hosam El Nagar
# Separated from RibasimResults.py file by Marnix van der vat
##############################################################


import os
import numpy as np
import math as math
import struct as struct
from datetime import datetime, timedelta


# define class to read his files
class HisFile:
    def __init__(self, fname):
        self.fname = fname
        self.hianame = self.fname.replace(".his", ".hia")

    def read(self):
        # try the hia file for long location names
        self.seghia = False
        try:
            f = open(self.hianame, "rt")
            for line in f:
                if line.strip() == "[Long Locations]":
                    self.seghia = True
                    self.longsegnums = list()
                    self.longsegnames = list()
                    for line in f:
                        iseg = int(line.split("=")[0])
                        longname = line.split("=")[1].strip()
                        self.longsegnums.append(iseg)
                        self.longsegnames.append(longname)
                        # print(iseg, longname)
            f.close()
        except Exception:
            self.seghia = False

        # try the hia file for long parameter names
        self.syshia = False
        try:
            f = open(self.hianame, "rt")
            for line in f:
                if line.strip() == "[Long Parameters]":
                    self.syshia = True
                    break
            if self.syshia:
                self.longsysnums = list()
                self.longsysnames = list()
                for line in f:
                    if line.strip() == "":
                        break
                    else:
                        isys = int(line.split("=")[0])
                        longname = line.split("=")[1].strip()
                        self.longsysnums.append(isys)
                        self.longsysnames.append(longname)
                        # print(isys, longname)
            f.close()
        except Exception:
            self.syshia = False

        # read the HIS file
        f = open(self.fname, "rb")
        self.moname = f.read(160).decode()
        year = int(self.moname[124:128])
        month = int(self.moname[129:131])
        day = int(self.moname[132:134])
        hour = int(self.moname[135:137])
        minute = int(self.moname[138:140])
        second = int(self.moname[141:143])
        self.startdate = datetime(year, month, day, hour, minute, second)
        if self.moname[157] == "s":
            self.scu = int(self.moname[150:157])
        else:
            self.scu = int(self.moname[150:158])
        # print self.startdate, self.scu
        self.nsys, = struct.unpack("i", f.read(4))
        self.nseg, = struct.unpack("i", f.read(4))
        # print self.nsys, self.nseg
        self.sysnames = list()
        for isys in range(self.nsys):
            sysnam = f.read(20).decode()
            self.sysnames.append(str.rstrip(sysnam))
            # print(isys, sysnam, self.sysnames[isys])
        self.segnames = list()
        self.segnums = list()
        for iseg in range(self.nseg):
            self.segnums.append(struct.unpack("i", f.read(4))[0])
            segnam = f.read(20).decode()
            self.segnames.append(str.rstrip(segnam))
            # print (iseg, segnam, self.segnums[iseg], self.segnames[iseg])
        size = os.path.getsize(self.fname)
        self.nstep = int((size - 168 - 20 * self.nsys - 24 * self.nseg) / (4 * (self.nsys * self.nseg + 1)))
        # print self.nstep
        self.datetime = list()
        self.data = np.zeros((self.nsys, self.nseg, self.nstep), "f")
        for lstep in range(self.nstep):
            fdays = struct.unpack("i", f.read(4))[0] * (self.scu / 86400.)
            iday = math.trunc(fdays)
            ihour = math.trunc((fdays - iday) * 24.)
            iminute = math.trunc((fdays - iday - ihour / 24.) * 60.)
            isecond = fdays * 86400 - 60 * math.trunc(fdays * 86400 / 60.)
            dt = self.startdate + timedelta(iday, ihour, iminute, isecond)
            self.datetime.append(dt)
            for iseg in range(self.nseg):
                for isys in range(self.nsys):
                    self.data[isys, iseg, lstep] = struct.unpack("f", f.read(4))[0]

    def getseries(self, sysnam, segnam):
        if self.syshia:
            i = self.longsysnames.index(sysnam)
            isys = self.longsysnums[i]
        else:
            isys = self.sysnames.index(sysnam)
        if self.seghia:
            i = self.longsegnames.index(segnam)
            iseg = self.longsegnums[i]
        else:
            iseg = self.segnames.index(segnam)
        # print isys, iseg
        res = np.zeros(self.nstep)
        for lstep in range(self.nstep):
            res[lstep] = self.data[isys, iseg, lstep]
        return res

    def gettimeseries(self, sysnam, segnam):
        if self.syshia:
            i = self.longsysnames.index(sysnam)
            isys = self.longsysnums[i]
        else:
            isys = self.sysnames.index(sysnam)
        if self.seghia:
            i = self.longsegnames.index(segnam)
            iseg = self.longsegnums[i]
        else:
            iseg = self.segnames.index(segnam)
        # print isys, iseg
        resdata = np.zeros((self.nstep))
        resdate = list()
        for lstep in range(self.nstep):
            resdate.append(self.datetime[lstep])
            resdata[lstep] = self.data[isys, iseg, lstep]
        return resdate, resdata

    def gettimeaverage(self, sysnam, segnam):
        if self.syshia:
            i = self.longsysnames.index(sysnam)
            isys = self.longsysnums[i]
        else:
            isys = self.sysnames.index(sysnam)
        if self.seghia:
            i = self.longsegnames.index(segnam)
            wqseg = self.longsegnums[i]
            wqsegnam = "Segment" + str(wqseg).rjust(7)
            iseg = self.segnames.index(wqsegnam)
        else:
            # print(self.segnames)
            iseg = self.segnames.index(segnam)
        # print isys, iseg
        total = 0.
        for lstep in range(self.nstep):
            total += self.data[isys, iseg, lstep]
        res = total / self.nstep
        return res
