import csv
import googlemaps
import re
import sqlite3

# Cаратовская область
# {'lat': 51.83692629999999, 'lng': 46.7539397}


gm = googlemaps.Client('AIzaSyD_UlRxu4BsQMT6M6PXu51-BqnFWvLGKjI')
conn = sqlite3.connect('test.db')
c = conn.cursor()

hospitals = []
with open('hospital.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='|')
    for row in spamreader:
        hospitals.append(row)


regex = re.compile(r'^[\d]+')
idx = 1
for i in hospitals:
    address = i[1]
    result = gm.geocode(address)
    if result == []:
        line = re.sub(regex, '', address)
        result = gm.geocode(line)
    coords = "; ".join(["%.2f" % v for v in result[0]['geometry']['location'].values()])

    sql = "INSERT INTO hospital VALUES (?, ?, ?, ?, ?, 1)"
    c.execute(sql, (idx, i[0], i[1], i[3], coords))
    idx += 1

conn.commit()
conn.close()
