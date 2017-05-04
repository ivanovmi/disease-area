import csv
import googlemaps
import re
import pprint
import sqlite3
import models

# Cаратовская область
# {'lat': 51.83692629999999, 'lng': 46.7539397}

#gm = googlemaps.Client('AIzaSyD_UlRxu4BsQMT6M6PXu51-BqnFWvLGKjI')
gm = googlemaps.Client("AIzaSyDlmB1OLGgiGVrEH16C7tL9qRZN_MDFqsQ")


def insert_to_db(csv_file):
    conn = sqlite3.connect('test.db')
    c = conn.cursor()

    hospitals = []
    with open(csv_file, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='|')
        for row in spamreader:
            hospitals.append(row)

    regex = re.compile(r'^[\d]+')
    idx = 1
    for i in hospitals:
        print(i)
        print(i[2])
        address = i[2]
        result = gm.geocode(address)
        if result == []:
            line = re.sub(regex, '', address)
            result = gm.geocode(line)
        try:
            coords = "; ".join(["%.2f" % v for v in result[0]['geometry']['location'].values()])
            print(coords)
        except IndexError:
            print("==============ERROR============:", "\n", result)
            coords = input("Enter coords: ")

        sql = "INSERT INTO hospital VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        try:
            c.execute(sql, (idx, i[0], i[1], i[2], i[4], i[5], i[6], i[7], coords, i[3]))
        except IndexError:
            print("=============ERROR==========:", "\n", i)
            sys.exit()
        idx += 1

    conn.commit()
    conn.close()

dis = '''Энгельсский район- 1746092
Турковский район - 1746088
Саратов - 3955288
Саратовский район - 1746046
Аркадакский район - 1746014
Аткарский район - 1746015
Базарно-Карабулакский район - 1746016
Балашовский район - 1746018
Вольский район - 1746020
Балаковский район - 1746017
Дергачевский район - 1746023
Екатериновский район - 1746025
Ершовский район - 1746026
Калининский район - 1746028
Красноармейский район - 1746029
Краснокутский район - 1746030
Краснопартизанский район - 1746031
Лысогорский район - 1746032
Марксовский район - 1746033
Новобурасский район - 1746035
Новоузенский район - 1746036
Озинский район - 1746037
Петровский район - 1746039
Питерский район - 1746040
Пугачевский район - 1746041
Ровенский район - 1746042
Романовский район - 1746043
Ртищевский район - 1746044
Самойловский район - 1746045
Советский район - 1746048
Татищевский район - 1746049
Федоровский район - 1746089
Воскресенский район - 1746021
Александрово-Гайский район - 1746013
Балтайский район - 1746019
Ивантеевский район - 1746027
Хвалынский район - 1746090
Перелюбский район - 1746038
Духовницкий район - 1746024
'''
_dis = '''Энгельсский район - 1746092
Турковский район - 1746088
Саратов - 3955288
Саратовский район - 1746046
Аркадакский район - 1746014
Аткарский район - 1746015
Базарно-Карабулакский район - 1746016
Балашовский район - 1746018
Вольский район - 1746020
Балаковский район - 1746017
Дергачевский район - 1746023
Екатериновский район - 1746025
Ершовский район - 1746026
Калининский район - 1746028
Красноармейский район - 1746029
Краснокутский район - 1746030
Краснопартизанский район - 1746031
Лысогорский район - 1746032
Марксовский район - 1746033
Новобурасский район - 1746035
Новоузенский район - 1746036
Озинский район - 1746037
Петровский район - 1746039
Питерский район - 1746040
Пугачевский район - 1746041
Ровенский район - 1746042
Романовский район - 1746043
Ртищевский район - 1746044
Самойловский район - 1746045
Советский район - 1746048
Татищевский район - 1746049
Федоровский район - 1746089
Воскресенский район - 1746021
Александрово-Гайский район - 1746013
Балтайский район - 1746019
Ивантеевский район - 1746027
Хвалынский район - 1746090
Перелюбский район - 1746038
Духовницкий район - 1746024
'''
types = '''Больницы взрослые
Больницы детские
Поликлиники взрослые
Поликлиники детские
Стоматологические поликлиники
Стоматологические поликлиники детские
Дом ребенка
Женская консультация
Родильные дома и перинатальные центры
Станция скорой медицинской помощи
Противотуберкулезные учреждения
Кожно-венерологические диспансеры
Наркологические учреждения
Онкологические диспансеры'''
import urllib
import json


def get_coord_by_id(idx):
    a = 'http://polygons.openstreetmap.fr/get_geojson.py?id={}&params=0'.format(idx)
    resp = urllib.request.urlopen(a)
    resp = json.loads(resp.read().decode(resp.info().get_param('charset') or 'utf-8'))
    coordinates = resp['geometries'][0]['coordinates']
    return coordinates[0][0]


def init_districts(a):
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    idx = 1
    for i in a.splitlines():
        arr = i.split(' - ')
        print(arr)
        coord = str(get_coord_by_id(arr[1]))
        sql = "INSERT INTO district VALUES (?, ?, ?)"
        c.execute(sql, (idx, arr[0], coord))
        idx += 1

    conn.commit()
    conn.close()


def init_types(csv_file):
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    types = []
    with open(csv_file, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter='|')
        for row in spamreader:
            types.append(row)

    idx = 1
    for i in types:
        sql = "INSERT INTO hospital_type VALUES (?, ?)"
        c.execute(sql, (idx, i[1]))
        idx += 1

    conn.commit()
    conn.close()


def gen_js(types, dis):
    data = []
    count = 1
    for i in types.splitlines():
        d = {}
        d['value'] = i
        d['id'] = str(count)
        count += 1
        d['data'] = []
        sec_count = 1
        for j in dis.splitlines():
            s = {}
            s['value'] = j.split('-')[0].strip()
            if s['value'] == 'Базарно':
                s['value'] = 'Базарно-Карабулакский район'
            elif s['value'] == 'Александрово':
                s['value'] = 'Александрово-Гайрайон'
            s['id'] = str(count)+'.'+str(sec_count)
            sec_count += 1
            d['data'].append(s)
        data.append(d)

    print(data)

gen_js(types, _dis)

print([(i.type_of.split(','), i.name,
        i.id,
        i.district) for i in models.Hospital.query.order_by().all()])
#import sys
#init_districts(dis)
#init_types('hospital_type.csv')
#insert_to_db(sys.argv[1])


