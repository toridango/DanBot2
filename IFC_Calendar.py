# -*- coding: utf-8 -*-
"""
Created on Sat Jun 02 00:31:56 2018

@author: richa
"""

monthNames = ["January", "February", "March", "April", "May", "June", "Sol", "July", "August", "September", "October", "November", "December", "New Year's Eve", "Leap day"]
gregorianDaysPerMonth = [31,28,31,30,31,30,31,31,30,31,30,31]

def isLeap(year):
    return (year%4 == 0 and year%100 != 0 and year%400 != 0)

def dayInYear(day, month, year):
    return day+ sum(gregorianDaysPerMonth[:month-1]) + (month>2 and isLeap(year))


def gregorian2IFC(day, month, year):
    yearIsLeap = isLeap(year)
    accDay = dayInYear(day,month,year)

    dayIFC = accDay%28

    monthIFC = ((accDay-dayIFC)/28) + 1

    if(yearIsLeap):
        if(monthIFC == 7 and dayIFC == 1):
            monthIFC = 6
            dayIFC = 29
        elif(accDay > 168):
            dayIFC -= 1

    if(dayIFC > 28 and not (dayIFC == 29 and (monthIFC == 13 or (yearIsLeap and monthIFC == 6)))):
        dayIFC -= 28
        monthIFC += 1

    if(dayIFC < 1):
        dayIFC += 28
        monthIFC -=1

    if (monthIFC == 14 and dayIFC == 1):
        monthIFC = 13;
        dayIFC = 29;

    return dayIFC,monthIFC,year
    
def getIFCStringDate(day,month,year):
    dayIFC,monthIFC,year = gregorian2IFC(day,month,year)

    dateSTR = str(dayIFC)+ " " + monthNames[monthIFC-1]+ " " + str(year)

    if(monthIFC == 13 and dayIFC==29):
        dateSTR =  monthNames[14-1]+ " " + str(year)

    if(monthIFC == 6 and dayIFC==29):
        dateSTR =  monthNames[15-1]+ " " + str(year)

    return dateSTR
