import csv
hospitals = []
with open('eggs.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='|')
    for row in spamreader:
        hospitals.append(row)

print(hospitals[1])

import sqlite3
conn = sqlite3.connect('test.db')
c = conn.cursor()
"""id|name|address|phone|coordinates|district_id"""
for i in hospitals:
    c.execute("INSERT INTO hospitals VALUES ('{}, {}, {}, {}, 1'.format(i[0], i[1], i[2])))"
conn.commit()
conn.close()
