import json
import base64
import io


def read_json(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return json.load(io.StringIO(decoded.decode("utf-8")))


import pandas as pd


def read_scv(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("cp1251")), delimiter=';')
    return df


def csv_to_json(df):
    dc = {}
    uName, serial = split_for_csv(list(df)[1])
    names = df.loc[0].tolist()

    for i in range(1, len(df.index)):
        temp = df.loc[i].tolist()
        dc[i] = {
            'Date': temp[0],
            'uName': uName,
            'serial': serial,
            'data': {lb: val for lb, val in list(zip(names[1:], temp[1:]))}
        }
    return dc


def split_for_csv(str1):
    return str1[:str1.find('(') - 1], str1[str1.find('(') + 1:str1.rfind(')')]


from datetime import datetime as dt, timedelta as td
from datetime import date


def sorting(y_temp, round_):
    if round_ == 'MAX':
        return max(y_temp)
    if round_ == 'MIN':
        return min(y_temp)
    else:
        return sum(y_temp) / len(y_temp)


def step(round_):
    if round_ == "day" or round_ == 'maximum' or round_ == 'minimum':
        return td(days=1)
    if round_ == 'hour':
        return td(hours=1)
    if round_ == 'hour3':
        return td(hours=3)
    if round_ == 'hour12':
        return td(hours=12)


def create_time_arr(round_, begin, end):
    x_arr = []
    begin = dt.strptime(begin, '%Y-%m-%d %H:%M:%S')
    end = dt.strptime(end, '%Y-%m-%d %H:%M:%S')
    st = step(round_)
    while td(begin.day, 0, 0, 0, begin.minute, begin.hour, 0).total_seconds() % st.total_seconds() != 0:
        begin -= td(minutes=1)
    while td(end.day, 0, 0, 0, end.minute, end.hour, 0).total_seconds() % st.total_seconds() != 0:
        end += td(minutes=1)

    while begin <= end:
        x_arr.append(begin)
        begin += st

    x_arr.append(begin + st)
    return x_arr


def sort(round_, x_arr, y_arr):
    if round_ == "none":
        return x_arr, y_arr

    date, temp, x_res, y_res, j = create_time_arr(round_, x_arr[0], x_arr[-1]), [], [], [], 0

    for i in range(len(x_arr)):

        if date[j + 1] > dt.strptime(x_arr[i], '%Y-%m-%d %H:%M:%S'):
            temp.append(y_arr[i])
        else:
            if len(temp) != 0:
                y_res.append(sorting(temp, round_))
                x_res.append(date[j])
                temp.clear()
            j += 1

    return x_res, y_res


def create_appliances_list(data):
    temp, res = {}, {}

    for item in data:

        if not "{} ({})".format(data[item]['uName'], data[item]['serial']) in temp:
            temp["{} ({})".format(data[item]['uName'], data[item]['serial'])] = create_devices(data, item)

    sorted_keys = sorted(temp, key=temp.get)
    for i in sorted_keys:
        res[i] = temp[i]

    return res


def create_devices(data, item):
    res = []
    for i in data[item]['data']:
        try:
            float(data[item]['data'][i])
            res.append("{}|{}|{}".format(data[item]['uName'], data[item]['serial'], i))
        except ValueError:
            continue
    return res


def get_info(sensor):
    sensor = sensor.split('|')
    return sensor[0], sensor[1], sensor[2]


def get_data(uName, serial, type, data):
    x_arr, y_arr = [], []
    for item in data:
        if data[item]['uName'] == uName and data[item]['serial'] == serial:
            try:
                x_arr.append(data[item]['Date'])
                y_arr.append(float(data[item]['data'][type]))

            except ValueError:
                continue

    return x_arr, y_arr


def temp_efficiency(t_arr, h_arr):
    res = []
    for i in range(len(t_arr)):
        res.append(t_arr[i] - 0.4 * (t_arr[i] - 10) * (1 - h_arr[i] / 100))

    return res


def heat(x_arr, y_arr, sens):
    heat_ = [
        {'heat': 'WTF', 'min': -36, 'max': -30, 'color': 'blue'},
        {'heat': 'extremely cold', 'min': -30, 'max': -24, 'color': 'DeepSkyBlue'},
        {'heat': 'very cold', 'min': -24, 'max': -12, 'color': 'Aqua'},
        {'heat': 'cold', 'min': -12, 'max': 0, 'color': 'MediumSpringGreen'},
        {'heat': 'moderately', 'min': 0, 'max': 6, 'color': 'lime'},
        {'heat': 'cool', 'min': 6, 'max': 12, 'color': 'YellowGreen'},
        {'heat': 'moderately warm', 'min': 12, 'max': 18, 'color': 'yellow'},
        {'heat': 'warm', 'min': 18, 'max': 24, 'color': 'orange'},
        {'heat': 'hot', 'min': 24, 'max': 30, 'color': 'OrangeRed'},
        {'heat': 'very hot', 'min': 30, 'max': 36, 'color': 'red'}
    ]
    min_, max_ = find_min_max(y_arr, sens)
    heat_ = correct_dict(heat_, min_, max_)
    print(heat_)
    dc, ann = [], []
    for i in range(len(heat_)):
        dc.append(dict(
            fillcolor=heat_[i]['color'], opacity=0.2, line={"width": 0}, type="rect",
            x0=x_arr[0], x1=x_arr[-1], xref="x",
            y0=heat_[i]['min'], y1=heat_[i]['max'], yref="y"))

        ann.append(dict(
            x=x_arr[0], y=(heat_[i]['max'] + heat_[i]['min']) / 2,
            arrowcolor="black", showarrow=False, font=dict(size=20, color='black'), text=heat_[i]['heat'], xref="x",
            yanchor="bottom", yref="y"))
    print(dc)
    return dc, ann


def find_min_max(y_arr, sens):
    res = y_arr.copy()
    res.extend(sens)
    return min(res), max(res)


def correct_dict(heat_, min_, max_):
    pos_min, pos_max = 0, -1
    for i in range(len(heat_)):
        if min_ < heat_[i]['max']:
            pos_min = i
            break
    for i in range(len(heat_)):
        if max_ < heat_[i]['max']:
            pos_max = i
            break

    heat_ = heat_[pos_min: pos_max + 1]
    heat_[0]['min'] = min_
    heat_[-1]['max'] = max_

    return heat_


# heat([], [-5, 6, 10, 8], [])

# GisMeteo


from bs4 import BeautifulSoup
import requests


def get_html_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 ' 
                      '(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    try:
        r = requests.get(url, headers=headers)
    except requests.exceptions.RequestException:
        return None
    else:
        if r.ok:
            return r.text


def create_Meteo_URL(date_begin):
    return "https://www.gismeteo.ru/diary/11441/{}/{}/".format(str(date_begin.year), str(date_begin.month))


def GetMeteo(date_begin, date_end):
    x_arr, y_temp, y_hum = [], [], []

    html = get_html_page(create_Meteo_URL(date_begin))
    data = BeautifulSoup(html, 'html.parser').find('table').find('tbody').findAll('tr')

    for row in data:
        day = row.findAll('td')
        x_arr.append(date(date_begin.year, date_begin.month, int(day[0].text)).strftime('%Y-%m-%d'))  # Дата
        y_temp.append((float(day[1].text) + float(day[6].text)) / 2)  # Температура
        y_hum.append((float(day[2].text) + float(day[7].text)) / 2)  # Давление

    if date_begin != date_end:
        newDate = date_begin + td(days=1)
        next_x, next_y_temp, next_y_hum = GetMeteo(newDate, date_end)
        x_arr.extend(next_x)
        y_temp.extend(next_y_temp)
        y_hum.extend(next_y_hum)

    return x_arr, y_temp, y_hum


#matrix
import numpy as np


def matrix(x_arr, y_arr):
    mat = [[], []]
    free = []
    for i in range(2):
        res = 0
        for j in range(len(y_arr)):
            res += (x_arr[j]**i)*y_arr[j]
        free.append(res)
    #free = np.asarray(free)
    print(free)
    for i in range(2):
        for j in range(2):
            res = 0
            for k in range(len(x_arr)):
                res += x_arr[k]**(i+j)
            mat[i].append(res)
    #mat = np.asarray(mat)
    print(mat, np.linalg.det(mat))
    #mat[0]=free
    #print(mat, np.linalg.det(mat))
    return list(np.linalg.solve(mat, free))