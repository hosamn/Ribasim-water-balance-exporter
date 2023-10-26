# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 11:36:06 2023

@author: vat
@edit: Hosam
    - added a loop over all case folders, you have to add their numbers to the list.
"""

import os
import hisreader
from datetime import datetime


# function to read word number wordn from line number linen in file filename
def getvfrf(filename, linen, wordn):
    with open(filename, "rt") as file:
        for iline in range(linen):
            line = file.readline()
        result = line.split()[wordn - 1]
        file.close()
        return result


# Get current dir & create output folder:
currdir = os.path.dirname(os.path.abspath(__file__))
respath = currdir + "\\results\\"
os.makedirs(os.path.dirname(respath), exist_ok=True)


for i in [24, 34, 35, 36, 38, 39]:              # <<<<<<<<<<<<<<<<<<<<<<  UPDATE, or add file reader
    case = i
    # case = "WORK"

    # list of units
    unitlst = [1, 2, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 62, 63, 65, 77, 78]

    # input file names
    if case == "WORK":
        descfolder = "CMTWORK"
    else:
        descfolder = case
    sumfile = "c:\\Ribasim7\\A4I.rbd\\{}\\summary.log".format(case)
    balfile = "c:\\Ribasim7\\A4I.rbd\\{}\\ribalans.log".format(case)
    airfile = "c:\\Ribasim7\\A4I.rbd\\{}\\OvAlWtBl.prt".format(case)
    hisfile = "c:\\Ribasim7\\A4I.rbd\\{}\\wq_rib.his".format(case)
    wqrib = hisreader.HisFile(hisfile)
    wqrib.read()
    hisfile = "c:\\Ribasim7\\A4I.rbd\\{}\\CltAgPro.his".format(case)
    yieldhis = hisreader.HisFile(hisfile)
    yieldhis.read()
    casedesc = "c:\\Ribasim7\\A4I.rbd\\{}\\casedesc.cmt".format(descfolder)

    # create output file name
    # respath = "c:\\Users\\vat\\OneDrive - Stichting Deltares\\11208232\\Ribasim\\results"
    filetimesec = os.path.getmtime(balfile)
    filetime = datetime.fromtimestamp(filetimesec)
    resfile = respath + "Case_" + str(case) + " - " + filetime.strftime("%y%m%d-%H%M") + ".txt"

    # get description from first two lines of casedesc.cmt
    with open(casedesc, "rt") as file:
        line = file.readline()
        sline = line.strip() + " "
        line = file.readline()
        sline += line
        file.close()

    # get salinity data from the wq_rib.his file
    sysnam = "TDS"
    salaver = 0.
    count = 0
    for cu in unitlst:
        if cu == 78:
            # Toska
            segnam = "Canal_361"
        else:
            segnam = "LFlow_PWS_Dom_{}".format(cu)
        sal = wqrib.gettimeaverage(sysnam, segnam)
        # print(cu, segnam, sal)
        salaver += sal
        count += 1

    # calculatye the average
    salaver = salaver / count

    # get wheat and rice production from CltAgPro.his
    rice = "Cr__7"
    wheat = "Cr_12"
    rice_yield = 0.
    wheat_yield = 0.
    sysnam = "Actual field level production [kg]"
    for segnam in yieldhis.segnames:
        if rice in segnam:
            yieldval = yieldhis.getseries(sysnam, segnam)
            # print(segnam, yieldval)
            rice_yield += yieldval[0] * 1e-6
        if wheat in segnam:
            yieldval = yieldhis.getseries(sysnam, segnam)
            # print(segnam, yieldval)
            wheat_yield += yieldval[0] * 1e-6

    # calculte system efficiency
    HADrel = float(getvfrf(balfile, 947, 5)) * 0.001
    irrisup = float(getvfrf(balfile, 957, 5)) * 0.001
    pwssup = float(getvfrf(balfile, 958, 6)) * 0.001
    fishsup = float(getvfrf(balfile, 959, 5)) * 0.001
    irriret = float(getvfrf(balfile, 949, 6)) * 0.001
    pwsret = float(getvfrf(balfile, 950, 7)) * 0.001
    gwret = float(getvfrf(balfile, 952, 8)) * 0.001
    gwstorincr = float(getvfrf(balfile, 956, 7)) * 0.001
    gwstordecr = float(getvfrf(balfile, 948, 6)) * 0.001
    syseff = (irrisup - irriret + pwssup - pwsret) / (HADrel + gwstordecr - gwstorincr) * 100

    # read numbers from RIBASIM output files and add them to sline
    sline += "                          water balance   model\n"
    sline += "HAD release                  61.30        {:.2f}\n".format(HADrel)
    sline += "Irrigation water demand      60.00        {:.2f}\n".format(float(getvfrf(sumfile, 168, 2)) * 0.001)
    sline += "Field evaporation            40.00        {:.2f}\n".format(float(getvfrf(airfile, 30, 2)) * 0.001)
    sline += "Irrigation water supply      60.43        {:.2f}\n".format(irrisup)
    sline += "Re-use shallow groundwater    3.88        {:.2f}\n".format(float(getvfrf(balfile, 974, 6)) * 0.001)
    sline += "Re-use drainage water        13.71        {:.2f}\n".format(float(getvfrf(balfile, 1032, 3)) * 0.001)
    sline += "PWS water demand             12.36        {:.2f}\n".format(float(getvfrf(sumfile, 585, 2)) * 0.001)
    sline += "PWS water supply             12.36        {:.2f}\n".format(pwssup)
    sline += "Fish pond water demand        4.20        {:.2f}\n".format(float(getvfrf(sumfile, 453, 2)) * 0.001)
    sline += "Fish pond water supply        4.20        {:.2f}\n".format(fishsup)
    sline += "Groundwater storage decrease              {:.2f}\n".format(gwstordecr)
    sline += "Groundwater storage increase              {:.2f}\n".format(gwstorincr)
    sline += "Outflow                      13.25        {:.2f}\n".format(float(getvfrf(balfile, 955, 4)) * 0.001)
    sline += "Average canal salinity (ppm)   243        {:.0f}\n".format(salaver)
    sline += "Wheat production (1000ton)   8,705        {:,.0f}\n".format(wheat_yield)
    sline += "Rice production (1000ton)    4,107        {:,.0f}\n".format(rice_yield)
    sline += "System efficiency (%)                     {:.0f}\n".format(syseff)

    # output to the screen
    print(sline)

    # outpout to file
    with open(resfile, "wt") as file:
        file.write(sline)
        file.close()
