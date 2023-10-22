# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 11:36:06 2023

@author: vat
"""

from datetime import datetime
import os
import numpy as np
import struct as struct
import math as math
from datetime import datetime, timedelta

case = "WORK"

#function to read word number wordn from line number linen in file filename
def getvfrf(filename,linen,wordn):
    with open(filename,'rt') as file:
        for iline in range(linen):
            line=file.readline()
        result=line.split()[wordn-1]
        file.close()
        return result

# define class to read his files
class HisFile:
    def __init__(self, fname):
        self.fname = fname
        self.hianame = self.fname.replace(".his",".hia")

    def read(self):
        #try the hia file for long location names
        self.seghia = False
        try:
            f = open(self.hianame,'rt')
            for line in f:
                if line.strip() == "[Long Locations]":
                    self.seghia = True
                    self.longsegnums=list()
                    self.longsegnames=list()                
                    for line in f:
                        iseg=int(line.split("=")[0])
                        longname=line.split("=")[1].strip()
                        self.longsegnums.append(iseg)                 
                        self.longsegnames.append(longname)
                        #print(iseg,longname)
            f.close()
        except:
            self.seghia = False

        #try the hia file for long parameter names
        self.syshia = False
        try:
            f = open(self.hianame,'rt')
            for line in f:
                if line.strip() == "[Long Parameters]":
                    self.syshia = True
                    break
            if self.syshia:
                self.longsysnums=list()
                self.longsysnames=list()                
                for line in f:
                    if line.strip() == "":
                        break
                    else:
                        isys=int(line.split("=")[0])
                        longname=line.split("=")[1].strip()
                        self.longsysnums.append(isys)                 
                        self.longsysnames.append(longname)
                        #print(isys,longname)
            f.close()
        except:
            self.syshia = False

        #read the HIS file
        f = open(self.fname, 'rb')
        self.moname = f.read(160).decode()
        year = int(self.moname[124:128])
        month = int(self.moname[129:131])
        day = int(self.moname[132:134])
        hour = int(self.moname[135:137])
        minute = int(self.moname[138:140])
        second = int(self.moname[141:143])
        self.startdate = datetime(year, month, day, hour, minute, second)
        if self.moname[157] == 's':
            self.scu = int(self.moname[150:157])
        else:
            self.scu = int(self.moname[150:158])
        #print self.startdate,self.scu
        self.nsys, = struct.unpack('i', f.read(4))
        self.nseg, = struct.unpack('i', f.read(4))
        #print self.nsys, self.nseg
        self.sysnames = list()
        for isys in range(self.nsys):
            sysnam=f.read(20).decode()
            self.sysnames.append(str.rstrip(sysnam))
            #print(isys,sysnam,self.sysnames[isys])
        self.segnames = list()
        self.segnums = list()
        for iseg in range(self.nseg):
            self.segnums.append(struct.unpack('i', f.read(4))[0])
            segnam=f.read(20).decode()
            self.segnames.append(str.rstrip(segnam))
            #print (iseg,segnam,self.segnums[iseg],self.segnames[iseg])
        size = os.path.getsize(self.fname)
        self.nstep = int((size - 168 - 20 * self.nsys - 24 * self.nseg) / (4 * (self.nsys * self.nseg + 1))     )
        #print self.nstep
        self.datetime = list()
        self.data = np.zeros((self.nsys, self.nseg, self.nstep), 'f')
        for lstep in range(self.nstep):
            fdays = struct.unpack('i', f.read(4))[0] * (self.scu / 86400.)
            iday = math.trunc(fdays)
            ihour = math.trunc((fdays - iday) * 24.)
            iminute = math.trunc((fdays - iday - ihour / 24.) * 60.)
            isecond = fdays * 86400 - 60 * math.trunc(fdays * 86400 / 60.)
            dt = self.startdate + timedelta(iday, ihour, iminute, isecond)
            self.datetime.append(dt)
            for iseg in range(self.nseg):
                for isys in range(self.nsys):
                    self.data[isys, iseg, lstep] = struct.unpack('f', f.read(4))[0]

    def getseries(self, sysnam, segnam):
        if self.syshia:
            i = self.longsysnames.index(sysnam) 
            isys = self.longsysnums[i]
        else:
            isys = self.sysnames.index(sysnam)
        if self.seghia:
            i = self.longsegnames.index(segnam)
            iseg=self.longsegnums[i]
        else:
            iseg = self.segnames.index(segnam)
        #print isys,iseg
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
            iseg=self.longsegnums[i]
        else:
            iseg = self.segnames.index(segnam)
       #print isys,iseg
        resdata = np.zeros((self.nstep))
        resdate = list()
        for lstep in range(self.nstep):
            resdate.append(self.datetime[lstep])
            resdata[lstep] = self.data[isys, iseg, lstep]
        return resdate, resdata
    
    def gettimeaverage(self,sysnam,segnam):
        if self.syshia:
            i = self.longsysnames.index(sysnam) 
            isys = self.longsysnums[i]
        else:
            isys = self.sysnames.index(sysnam)
        if self.seghia:
            i = self.longsegnames.index(segnam)
            wqseg=self.longsegnums[i]
            wqsegnam="Segment" + str(wqseg).rjust(7)
            iseg = self.segnames.index(wqsegnam)
        else:
            iseg = self.segnames.index(segnam)
        #print isys,iseg
        total=0.
        for lstep in range(self.nstep):
            total += self.data[isys, iseg, lstep]
        res = total / self.nstep
        return res

#list of units
unitlst=[1,2,6,7,8,9,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,62,63,65,77,78] 

#input file names
if case =="WORK":
    descfolder = "CMTWORK"
else:
    descfolder = case
sumfile = 'c:\\Ribasim7\\A4I.rbd\\{}\\summary.log'.format(case)
balfile = 'c:\\Ribasim7\\A4I.rbd\\{}\\ribalans.log'.format(case)
airfile = 'c:\\Ribasim7\\A4I.rbd\\{}\\OvAlWtBl.prt'.format(case)
hisfile = 'c:\\Ribasim7\\A4I.rbd\\{}\\wq_rib.his'.format(case)
wqrib=HisFile(hisfile)
wqrib.read()
hisfile = 'c:\\Ribasim7\\A4I.rbd\\{}\\CltAgPro.his'.format(case)
yieldhis=HisFile(hisfile)
yieldhis.read()
casedesc= 'c:\\Ribasim7\\A4I.rbd\\{}\\casedesc.cmt'.format(descfolder)
#create output file name
respath = 'c:\\Users\\vat\\OneDrive - Stichting Deltares\\11208232\\Ribasim\\results'
filetimesec=os.path.getmtime(balfile)
filetime=datetime.fromtimestamp(filetimesec)
resfile = respath + '\\RibasimResults' + filetime.strftime("%y%m%d-%H%M") + '.txt'

#get description from first two lines of casedesc.cmt
with open(casedesc,'rt') as file:
    line=file.readline()
    sline = line.strip() + ' '
    line=file.readline()
    sline += line
    file.close()

#get salinity data from the wq_rib.his file
sysnam="TDS"
salaver=0.
count=0
for cu in unitlst:
    if cu == 78:
        #Toska
        segnam= "Canal_361"
    else:
        segnam= "LFlow_PWS_Dom_{}".format(cu)
    sal=wqrib.gettimeaverage(sysnam, segnam)
    #print(cu,segnam,sal)
    salaver += sal
    count += 1

#calculatye the average
salaver = salaver / count    

#get wheat and rice production from CltAgPro.his
rice="Cr__7"
wheat="Cr_12"
rice_yield=0.
wheat_yield = 0.
sysnam = "Actual field level production [kg]"
for segnam in yieldhis.segnames:
    if rice in segnam:
        yieldval = yieldhis.getseries(sysnam, segnam)
        #print(segnam,yieldval)
        rice_yield += yieldval[0] * 1e-6
    if wheat in segnam:
        yieldval = yieldhis.getseries(sysnam, segnam)
        #print(segnam,yieldval)
        wheat_yield += yieldval[0] * 1e-6

#calculte system efficiency
HADrel = float(getvfrf(balfile,947,5))*0.001
irrisup=float(getvfrf(balfile,957,5))*0.001
pwssup = float(getvfrf(balfile,958,6))*0.001
fishsup = float(getvfrf(balfile,959,5))*0.001
irriret= float(getvfrf(balfile,949,6))*0.001
pwsret= float(getvfrf(balfile,950,7))*0.001
gwret= float(getvfrf(balfile,952,8))*0.001
gwstorincr = float(getvfrf(balfile,956,7))*0.001
gwstordecr = float(getvfrf(balfile,948,6))*0.001
syseff = (irrisup-irriret+pwssup-pwsret) / (HADrel+gwstordecr-gwstorincr)*100

#read numbers from RIBASIM output files and add them to sline
sline += '                          water balance      model\n'
sline += 'HAD release                  61.30           {:.2f}\n'.format(HADrel)
sline += 'Irrigation water demand      60.00           {:.2f}\n'.format(float(getvfrf(sumfile,168,2))*0.001)
sline += 'Field evaporation            40.00           {:.2f}\n'.format(float(getvfrf(airfile,30,2))*0.001)
sline += 'Irrigation water supply      60.43           {:.2f}\n'.format(irrisup)
sline += 'Re-use shallow groundwater    3.88           {:.2f}\n'.format(float(getvfrf(balfile,974,6))*0.001)
sline += 'Re-use drainage water        13.71           {:.2f}\n'.format(float(getvfrf(balfile,1032,3))*0.001)
sline += 'PWS water demand             12.36           {:.2f}\n'.format(float(getvfrf(sumfile,585,2))*0.001)
sline += 'PWS water supply             12.36           {:.2f}\n'.format(pwssup)
sline += 'Fish pond water demand        4.20           {:.2f}\n'.format(float(getvfrf(sumfile,453,2))*0.001)
sline += 'Fish pond water supply        4.20           {:.2f}\n'.format(fishsup)
sline += 'Groundwater storage decrease                 {:.2f}\n'.format(gwstordecr)
sline += 'Groundwater storage increase                 {:.2f}\n'.format(gwstorincr)
sline += 'Outflow                      13.25           {:.2f}\n'.format(float(getvfrf(balfile,955,4))*0.001)
sline += 'Average canal salinity (ppm)   243           {:.0f}\n'.format(salaver)
sline += 'Wheat production (1000ton)   8,705           {:,.0f}\n'.format(wheat_yield)
sline += 'Rice production (1000ton)    4,107           {:,.0f}\n'.format(rice_yield)
sline += 'System efficiency (%)                        {:.0f}\n'.format(syseff)

#output to the screen
print(sline)

#outpout to file
with open(resfile,'wt') as file:
    file.write(sline)
    file.close()