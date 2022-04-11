import json
from typing import Callable

from matplotlib import cycler
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import os

import uuid

# pyplot config #
plt.rcParams['axes.facecolor'] = 'black'
# plt.rcParams['axes.labelcolor'] = 'white'
plt.rcParams['xtick.color'] = 'white'
plt.rcParams['ytick.color'] = 'white'
plt.rcParams['figure.facecolor'] = 'black'
# plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.prop_cycle'] = cycler('color', ['31B4FF'])

plt.rcParams['figure.figsize'] = (19, 10.8)
plt.rcParams['savefig.dpi'] = 128
plt.rcParams['savefig.bbox'] = 'tight'

# constants #
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
MAX_LABELS = 35
FIG_PATH = "figures"


# conversion functions #

def datetime_to_date(datetime: dt.datetime) -> str:
    return str(f"{datetime.year:04d}-{datetime.month:02d}-{datetime.day:02d}-{datetime.hour:02d}")


def date_to_datetime(date: str) -> dt.datetime:
    year, month, day, hour = map(int, date.split("-"))
    return dt.datetime(year, month, day, hour)


def timestamp_to_date(timestamp: int, bucket=None) -> str:
    datetime = dt.datetime.fromtimestamp(timestamp)
    end = {
        None: 4,
        "days": 3,
        "months": 2,
        "years": 1,
    }[bucket]
    date = datetime_to_date(datetime)
    bucket_date = "-".join(date.split("-")[:end])
    return bucket_date


# value computation functions #

def filter_activity(activity: dict, start_date: str, end_date: str) -> dict:
    activity_tuples = list(activity.items())
    # append start date and end date to the tuples in a way that they'll be in the proper boundaries
    # note: python's sort is stable
    if start_date:
        activity_tuples.insert(0, (start_date, -1))
    if end_date:
        activity_tuples.append((end_date, -1))

    activity_tuples.sort(key=lambda t: t[0])

    # locate the boundaries by searching for the inserted tuples
    start_idx = 0
    end_idx = len(activity_tuples)

    if start_date:
        for i, (_, count) in enumerate(activity_tuples):
            if count == -1:
                start_idx = i + 1
                break

    if end_date:
        for i, (_, count) in enumerate(activity_tuples[start_idx:]):
            if count == -1:
                end_idx = start_idx + i
                break

    # slice tuple list and transform back to list
    filtered_activity_tuples = activity_tuples[start_idx:end_idx]
    filtered_activity = {k: v for k, v in filtered_activity_tuples}

    return filtered_activity


def calc_hour_activity(activity: dict) -> dict:
    hour_activity = {k: 0 for k in range(24)}
    for key in activity:
        hour_activity[int(key.split("-")[-1])] += activity[key]
    return hour_activity


def calc_weekday_activity(activity: dict) -> dict:
    weekday_activity = {k: 0 for k in range(7)}
    for key in activity:
        year, month, day, _ = map(int, key.split("-"))
        weekday = dt.datetime(year, month, day).weekday()
        weekday_activity[weekday] += activity[key]
    return weekday_activity


def calc_month_activity(activity: dict) -> dict:
    month_activity = {k: 0 for k in range(1, 12 + 1)}
    for key in activity:
        _, month, _, _ = key.split("-")
        month_activity[int(month)] += activity[key]
    return month_activity


def bucket_days(date: str) -> str:
    year, month, day, _ = date.split("-")
    return "-".join([year, month, day, "00"])


def bucket_months(date: str) -> str:
    year, month, _, _ = date.split("-")
    return "-".join([year, month, "01", "00"])


def bucket_years(date: str) -> str:
    year, _, _, _ = date.split("-")
    return "-".join([year, "01", "01", "00"])


def bucket_dates(activity: dict, bucket_func: Callable[[str], str]) -> dict:
    new_activity_tuples = {}
    for date, count in activity.items():
        new_date = bucket_func(date)
        if new_date not in new_activity_tuples:
            new_activity_tuples[new_date] = 0
        new_activity_tuples[new_date] += count
    return new_activity_tuples


# plot functions #

def new_fig_path():
    return os.path.join(FIG_PATH, dt.datetime.now().strftime("%Y%m%d%S%f") + ".png")


def plot_hour_activity(activity: dict) -> str:
    x = list(activity.keys())
    y = list(activity.values())

    # loop some values on the left and right so that the interpolation is calculated better
    xloop = [-3, -2, -1, *x, 24, 25, 26]
    yloop = [y[-3], y[-2], y[-1], *y, y[0], y[1], y[2]]

    # cubic interpolation
    f = interp1d(np.array(xloop, dtype=np.float), np.array(yloop, dtype=np.int), kind='cubic')
    xinterp = np.linspace(0, 24, num=24 * 60)

    # plot
    plt.plot(xinterp, f(xinterp))
    plt.xticks(range(24), [f"{i}:00" for i in range(24)])
    # plt.tick_params(axis='x', bottom=False)
    # plt.tick_params(axis='y', left=False, labelleft=False)
    plt.vlines(x=x, ymin=0, ymax=y, colors="gray", ls=':')
    fig_path = new_fig_path()
    plt.savefig(fig_path)
    plt.close()

    return fig_path


def plot_weekday_activity(activity: dict) -> str:
    return plot_discrete_activity(activity, labels=WEEKDAYS)


def plot_month_activity(activity: dict) -> str:
    return plot_discrete_activity(activity, labels=MONTHS)


def plot_discrete_activity(activity: dict, labels: iter) -> str:
    x = list(activity.keys())
    y = list(activity.values())

    plt.bar(x, y)
    plt.xticks(x, labels)
    fig_path = new_fig_path()
    plt.savefig(fig_path)
    plt.close()

    return fig_path


def plot_activity_evolution(activity: dict, bucket="days") -> str:
    # merge dates into buckets depending on bucket argument
    bucket_func = {
        "days": bucket_days,
        "months": bucket_months,
        "years": bucket_years,
    }[bucket]
    activity = bucket_dates(activity, bucket_func)

    # transform to tuples and sort
    activity_tuples = list(activity.items())
    activity_tuples.sort(key=lambda t: t[0])

    # calculate diff between dates, this is necessary to generate the x linspace
    start_datetime = date_to_datetime(activity_tuples[0][0])
    end_datetime = date_to_datetime(activity_tuples[-1][0])
    datetime_diff = end_datetime - start_datetime

    # generate x linspace depending on buckets
    # this is so that buckets without any data are shown as having 0 messages
    if bucket == "days":
        n = datetime_diff.days
        x = [int((start_datetime + dt.timedelta(days=i)).timestamp()) for i in range(n + 1)]
        assert x[-1] == end_datetime.timestamp()
    elif bucket == "months":
        n = (end_datetime.year - start_datetime.year) * 12 + (end_datetime.month - start_datetime.month)
        x = []
        curr_year = start_datetime.year
        curr_month = start_datetime.month
        for i in range(n + 1):
            x.append(dt.datetime(curr_year, curr_month, 1).timestamp())
            curr_month += 1
            if curr_month == 13:
                curr_year += 1
                curr_month = 1
        assert x[-1] == end_datetime.timestamp()
    elif bucket == "years":
        n = end_datetime.year - start_datetime.year
        x = [dt.datetime(start_datetime.year + i, 1, 1).timestamp() for i in range(n + 1)]
        assert x[-1] == end_datetime.timestamp()
    else:
        raise ValueError(f"Unknown bucket: {bucket}")

    # add values to the generated linspace
    xy_dict = {k: 0 for k in x}
    for date, count in activity_tuples:
        xy_dict[int(date_to_datetime(date).timestamp())] = count

    x = list(xy_dict.keys())
    y = list(xy_dict.values())

    # if there are too many labels, reduce them evenly
    if len(x) > MAX_LABELS:
        diff = x[-1] - x[0]
        step = diff / MAX_LABELS
        label_x = [int(x[0] + step * i) for i in range(MAX_LABELS)]
    else:
        label_x = x

    label_str = list(map(lambda d: timestamp_to_date(d, bucket=bucket), label_x))
    # rotate labels vertically in case there are a lot (4 discrete levels)
    label_rot = 70 * (round(4 * (len(label_x) / MAX_LABELS)) / 4)

    # cubic interpolation
    f = interp1d(np.array(x, dtype=np.float), np.array(y, dtype=np.int), kind='cubic')
    xinterp = np.linspace(x[0], x[-1], num=len(x) * 25)

    plt.plot(xinterp, f(xinterp))
    plt.xticks(label_x, label_str, rotation=label_rot)
    fig_path = new_fig_path()
    plt.savefig(fig_path)
    plt.close()

    return fig_path


def main():
    with open("tally.json") as f:
        activity = json.load(f)
    activity = filter_activity(activity, "2020-01-01-00", "2020-02-01-00")
    # print(activity)
    # hour_activity = calc_hour_activity(activity)
    # print(hour_activity)
    # plot_hour_activity(hour_activity)
    # weekday_activity = calc_weekday_activity(activity)
    # print(weekday_activity)
    # plot_discrete_activity(weekday_activity, labels=WEEKDAYS)
    # month_activity = calc_month_activity(activity)
    # print(month_activity)
    # plot_discrete_activity(month_activity, labels=MONTHS)
    # plot_full_activity(activity)
    plot_activity_evolution(activity, bucket="days")
    plot_activity_evolution(activity, bucket="months")
    plot_activity_evolution(activity, bucket="years")


if __name__ == "__main__":
    main()
