import xlrd
import re
import sys
import models

districts = """
Александрово-Гайский
Аркадакский
Аткарский
Базарно-карабулакский
Балаковский
Балашовский
Балтайский
Вольский
Воскресенский
Дергачевский
Духовницкий
Екатериновский
Ершовский
Ивантеевский
Калининский
Красноармейский
Краснокутский
Краснопартизанский
Лысогорский
Марксовский
Новобурасский
Новоузенский
Озинский
Перелюбский
Петровский
Питерский
Пугачевский
Ровенский
Романовский
Ртищевский
Самойловский
Саратовский
Советский
Татищевский
Турковский
Федоровский
Хвалынский
Энгельсский
"""


def get_sheet(xls_file, sheet_number=0):
    xls = xlrd.open_workbook(xls_file)
    sheet = xls.sheet_by_index(sheet_number)
    return sheet


def parse_marriage(xls_file, districts):
    sheet = get_sheet(xls_file)
    results = list()
    for row in range(2, sheet.nrows):
        result = dict()
        result["year"] = sheet.row_values(0)[0]
        r = sheet.row_values(row)
        if r[0] == "Базарнокарабулакский":
            r[0] = "Базарно-Карабулакский"
        elif r[0] == "Энгельсский":
            r[0] = "Энгельский"
        elif r[0] == "Ровенский":
            r[0] = "Ровновский"
        if r[0].strip() != "г.Саратов":
            district_id = districts.index(r[0].strip()+" район")+1
        else:
            district_id = 3
        result["district_id"] = district_id
        result["marriage"], result["marriage_1000"], result["divorce"], result["divorce_1000"] = r[1:]
        results.append(result)
    return results


def parse_migration(xls_file, districts):
    sheet = get_sheet(xls_file)
    results = list()
    for row in range(3, sheet.nrows):
        result = dict()
        result["year"] = sheet.row_values(0)[0]
        r = sheet.row_values(row)
        if r[0] == "Базарнокарабулакский":
            r[0] = "Базарно-Карабулакский"
        elif r[0] == "Энгельсский":
            r[0] = "Энгельский"
        elif r[0] == "Ровенский":
            r[0] = "Ровновский"
        if r[0].strip() != "г.Саратов":
            district_id = districts.index(r[0].strip() + " район") + 1
        else:
            district_id = 3
        result["district_id"] = district_id
        result["added"], result["substituded"], result["diff"] = r[1:]
        results.append(result)
    return results


def parse_mortality(xls_file, districts):
    sheet = get_sheet(xls_file)
    results = list()
    for row in range(4, sheet.nrows):
        result = dict()
        result["year"] = sheet.row_values(0)[0]
        r = sheet.row_values(row)
        if r[0] == "Базарнокарабулакский":
            r[0] = "Базарно-Карабулакский"
        elif r[0] == "Энгельсский":
            r[0] = "Энгельский"
        elif r[0] == "Ровенский":
            r[0] = "Ровновский"
        if r[0].strip() != "г.Саратов":
            district_id = districts.index(r[0].strip() + " район") + 1
        else:
            district_id = 3
        result["district_id"] = district_id
        result["all_population"], result["city_population"], result["village_population"], result["died_on_1000_borned"], result["died_under_1"] = [i if i != "-" else 0 for i in r[1:] ]

        results.append(result)
    return results


def parse_population(xls_file, districts):
    sheet = get_sheet(xls_file)
    results = list()
    for row in range(4, sheet.nrows-5):
        result = dict()
        result["year"] = int(sheet.row_values(0)[0].split('.')[-1].split()[0])
        r = sheet.row_values(row)
        if r[0] == "Базарнокарабулакский" or r[0] == "Б.КАРАБУЛАКСКИЙ":
            r[0] = "Базарно-Карабулакский"
        elif r[0] == "Энгельсский" or r[0] == "ЭНГЕЛЬС + pайон":
            r[0] = "Энгельский"
        elif r[0] == "Ровенский" or r[0] == "РОВЕНСКИЙ":
            r[0] = "Ровновский"
        elif r[0] == "АЛ.ГАЙСКИЙ":
            r[0] = "Александрово-Гайский"
        elif r[0] == "ОЗИНКИНСКИЙ":
            r[0] = "Озинский"
        elif r[0] == "ТАТИЩЕВСКИЙ+п.Светлый":
            r[0] = "Татищевский"
        elif r[0] == "АТКАРСК":
            r[0] = "Аткарский"
        elif r[0] == "БАЛАКОВО(+район)":
            r[0] = "Балаковский"
        elif r[0] == "БАЛАШОВ + pайон":
            r[0] = "Балашовский"
        elif r[0] == "ВОЛЬСК+район+Шиханы":
            r[0] = "Вольский"
        elif r[0] == "КРАСНОАРМЕЙСК":
            r[0] = "Красноармейский"
        elif r[0] == "МАРКС":
            r[0] = "Марксовский"
        elif r[0] == "САРАТОВ":
            r[0] = "г.Саратов"
        elif r[0] == "ХВАЛЫНСК":
            r[0] = "Хвалынский"

        if r[0].strip() != "г.Саратов":
            district_id = districts.index(r[0].title().strip() + " район") + 1
        else:
            district_id = 3
        result["district_id"] = district_id

        result["all"], result["men"], result["women"], result["children"], result["adults"], result["employable"], result["employable_men"], result["employable_women"] = r[1], r[2], r[3], r[4]+r[5]+r[8], r[7], r[11], r[12], r[13]

        results.append(result)
    return results


def parse_reprod(xls_file, districts):
    sheet = get_sheet(xls_file)
    results = list()
    for row in range(4, sheet.nrows):
        result = dict()
        result["year"] = sheet.row_values(0)[0]
        r = sheet.row_values(row)
        if r[0].startswith("Базарнокарабулакский"):
            r[0] = "Базарно-Карабулакский район"
        elif r[0].startswith("Энгельсский"):
            r[0] = "Энгельский район"
        elif r[0].startswith("Ровенский"):
            r[0] = "Ровновский район"
        if r[0].strip() != "г.Саратов":
            try:
                district_id = districts.index(r[0].strip()) + 1
            except ValueError:
                # TODO: weak place
                continue
        else:
            district_id = 3
        result["district_id"] = district_id
        result["borned"], result["borned_1000"], result["died"], result["died_1000"], result["nat_add"], result["nat_add_1000"] = r[1:]
        results.append(result)
    return results

if __name__ == "__main__":
    all_districts = list(map(str,
                             models.District.query.order_by(models.District.id).all()))
    parse_reprod(sys.argv[1], all_districts)