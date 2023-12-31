# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 11:36:06 2023

@author: vat
@edit: Hosam
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

model = "c:\\Ribasim7\\A4I.rbd\\"


# # Traverse the model  folder and find all case folders:
cases = [i for i in range(99) if os.path.exists(model + str(i))]

for case in cases:
    case = str(case)
    # case = "WORK"

    # list of units
    culist = [1, 2, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 62, 63, 65, 77, 78]

    # input file names
    if case == "WORK":
        descfolder = "CMTWORK"
    else:
        descfolder = case

    sumfile = model + case + "\\summary.log"
    balfile = model + case + "\\ribalans.log"
    airfile = model + case + "\\OvAlWtBl.prt"

    wqhisfile = model + case + "\\wq_rib.his"
    wqrib = hisreader.HisFile(wqhisfile)
    wqrib.read()

    yldhisfile = model + case + "\\CltAgPro.his"
    yieldhis = hisreader.HisFile(yldhisfile)
    yieldhis.read()

    casedesc = model + descfolder + "\\casedesc.cmt"

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
    for cu in culist:
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

    # # Setting some starting points to navigate text files:
    balfile_loc = 947
    sumfile_loc = 168
    airfile_loc = 30

    # calculte system efficiency
    HAD_rel = float(getvfrf(balfile, balfile_loc + 0, 5)) * 0.001
    irrisup = float(getvfrf(balfile, balfile_loc + 10, 5)) * 0.001
    pwssupp = float(getvfrf(balfile, balfile_loc + 11, 6)) * 0.001
    fishsup = float(getvfrf(balfile, balfile_loc + 12, 5)) * 0.001
    irrretr = float(getvfrf(balfile, balfile_loc + 2, 6)) * 0.001
    pwsretr = float(getvfrf(balfile, balfile_loc + 3, 7)) * 0.001
    gwret__ = float(getvfrf(balfile, balfile_loc + 5, 8)) * 0.001
    gw_incr = float(getvfrf(balfile, balfile_loc + 9, 7)) * 0.001
    gw_decr = float(getvfrf(balfile, balfile_loc + 1, 6)) * 0.001
    sys_eff = (irrisup - irrretr + pwssupp - pwsretr) / (HAD_rel + gw_decr - gw_incr) * 100

    gwReuse = float(getvfrf(balfile, balfile_loc + 27, 6)) * 0.001
    drReuse = float(getvfrf(balfile, balfile_loc + 85, 3)) * 0.001
    outflow = float(getvfrf(balfile, balfile_loc + 8, 4)) * 0.001
    irriDem = float(getvfrf(sumfile, sumfile_loc + 0, 2)) * 0.001
    pwd_Dem = float(getvfrf(sumfile, sumfile_loc + 417, 2)) * 0.001
    fsh_Dem = float(getvfrf(sumfile, sumfile_loc + 285, 2)) * 0.001
    fieldEv = float(getvfrf(airfile, airfile_loc + 0, 2)) * 0.001


    # read numbers from RIBASIM output files and add them to sline
    sline += "                         Water Balance    Model\n"
    sline += "HAD release                  61.30        {:.2f}\n".format(HAD_rel)
    sline += "Irrigation water demand      60.00        {:.2f}\n".format(irriDem)
    sline += "Field evaporation            40.00        {:.2f}\n".format(fieldEv)
    sline += "Irrigation water supply      60.43        {:.2f}\n".format(irrisup)
    sline += "Re-use shallow groundwater    3.88        {:.2f}\n".format(gwReuse)
    sline += "Re-use drainage water        13.71        {:.2f}\n".format(drReuse)
    sline += "PWS water demand             12.36        {:.2f}\n".format(pwd_Dem)
    sline += "PWS water supply             12.36        {:.2f}\n".format(pwssupp)
    sline += "Fish pond water demand        4.20        {:.2f}\n".format(fsh_Dem)
    sline += "Fish pond water supply        4.20        {:.2f}\n".format(fishsup)
    sline += "Groundwater storage decrease              {:.2f}\n".format(gw_decr)
    sline += "Groundwater storage increase              {:.2f}\n".format(gw_incr)
    sline += "Outflow                      13.25        {:.2f}\n".format(outflow)
    sline += "Average canal salinity (ppm)   243        {:.0f}\n".format(salaver)
    sline += "Wheat production (1000ton)   8,705        {:,.0f}\n".format(wheat_yield)
    sline += "Rice production (1000ton)    4,107        {:,.0f}\n".format(rice_yield)
    sline += "System efficiency (%)                     {:.0f}\n".format(sys_eff)

    # output to the screen
    print(sline)

    # outpout to file
    with open(resfile, "wt") as file:
        file.write(sline)
        file.close()
