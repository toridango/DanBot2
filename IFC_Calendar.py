"""
Created on Sat Jun 02 00:31:56 2018

@author: richa
"""

monthNames = ["January", "February", "March", "April", "May", "June", "Sol", "July", "August", "September", "October",
              "November", "December", "New Year's Eve", "Leap day"]
gregorianDaysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def is_leap(year):
    return year % 4 == 0 and year % 100 != 0 and year % 400 != 0


def day_in_year(day, month, year):
    return day + sum(gregorianDaysPerMonth[:month - 1]) + (month > 2 and is_leap(year))


def gregorian2ifc(day, month, year):
    year_is_leap = is_leap(year)
    acc_day = day_in_year(day, month, year)

    day_ifc = acc_day % 28

    month_ifc = ((acc_day - day_ifc) // 28) + 1

    if year_is_leap:
        if month_ifc == 7 and day_ifc == 1:
            month_ifc = 6
            day_ifc = 29
        elif acc_day > 168:
            day_ifc -= 1

    if day_ifc > 28 and not (day_ifc == 29 and (month_ifc == 13 or (year_is_leap and month_ifc == 6))):
        day_ifc -= 28
        month_ifc += 1

    if day_ifc < 1:
        day_ifc += 28
        month_ifc -= 1

    if month_ifc == 14 and day_ifc == 1:
        month_ifc = 13
        day_ifc = 29

    return day_ifc, month_ifc, year


def get_ifc_string_date(day, month, year):
    day_ifc, month_ifc, year = gregorian2ifc(day, month, year)

    date_str = str(day_ifc) + " " + monthNames[month_ifc - 1] + " " + str(year)

    if month_ifc == 13 and day_ifc == 29:
        date_str = monthNames[14 - 1] + " " + str(year)

    if month_ifc == 6 and day_ifc == 29:
        date_str = monthNames[15 - 1] + " " + str(year)

    return date_str
