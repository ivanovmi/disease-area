import xlrd
import sys
import models


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
        result["marriage"], result["divorce"] = r[1:]
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


def parse_nathality(xls_file, districts):
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
        result["_15_17"], result["_18_24"], result["_25_29"], result["_30_34"], result["_35_older"] = [i if i != "-" else 0 for i in r[2:]]

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
        result["all_population"], result["city_population"], result["village_population"], result["died_under_1"] = [i if i != "-" else 0 for i in r[1:] ]

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

        result["all"], result["men"], result["women"], result["children"], result["teenagers"], result["adults"], result["employable"], result["country_population"] = r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8]

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
        result["borned"], result["died"], result["nat_add"] = r[1:]
        results.append(result)
    return results


def parse_diseases(xls_file, districts, diseases, db):
    child_sheet = get_sheet(xls_file)
    teen_sheet = get_sheet(xls_file, 1)
    adult_sheet = get_sheet(xls_file, 2)
    results = list()
    if child_sheet.row_values(0)[4].split()[1] == 'общей':
        is_f = False
    else:
        is_f = True
    ds = child_sheet.row_values(1)[5:]
    years = child_sheet.row_values(2)[2:5]
    c = 1
    for d in range(0, len(ds), 3):
        result = dict()
        result['is_first'] = is_f
        if ds[d] == 'БOЛEЗHИ КРОВИ,КРОВЕТВОР.ОРГАHОВ И ОТД.HАРУШЕHИЯ,ВОВЛЕК.ИММУHHЫЙ МЕХ-':
            ds[d] = 'БOЛEЗHИ КРОВИ, КРОВЕТВОРНЫХ ОРГАHОВ И ОТД.HАРУШЕHИЯ, ВОВЛЕКАЮЩИЕ ИММУHHЫЙ МЕХАНИЗМ'
        elif ds[d] == 'БOЛEЗHИ ЭHДОКРИHHОЙ СИСТЕМЫ,РАСС-ВА ПИТАHИЯ И HАРУШЕHИЯ ОБМЕHА ВЕЩЕС':
            ds[d] = 'БOЛEЗHИ ЭHДОКРИHHОЙ СИСТЕМЫ, РАССТРОЙСТВА ПИТАHИЯ И HАРУШЕHИЯ ОБМЕHА ВЕЩЕСТВ'
        elif ds[d] == 'БOЛEЗHИ KOЖИ И ПOДKOЖHOЙ KЛETЧATKИ':
            ds[d] = 'БОЛЕЗНИ КОЖИ И ПОДКОЖНОЙ КЛЕТЧАТКИ'
        elif ds[d] == 'ВРОЖДЕH.АHОМАЛИИ(ПОРОКИ РАЗВ.),ДЕФОРМАЦИИ И ХРОМОСОМHЫЕ HАРУШ.':
            ds[d] = 'ВРОЖДЕHНЫЕ АHОМАЛИИ (ПОРОКИ РАЗВИТИЯ), ДЕФОРМАЦИИ И ХРОМОСОМHЫЕ HАРУШЕНИЯ'
        elif ds[d] == 'СИМП.,ПРИЗH.И ОТКЛОH.ОТ HОРМЫ,ВЫЯВ.ПРИ КЛИH.И ЛАБ.ИССЛ.HЕ КЛАССИФ.В':
            ds[d] = 'СИМПТОМЫ, ПРИЗHАКИ И ОТКЛОHЕНИЯ ОТ HОРМЫ, ВЫЯВЛЕННЫЕ ПРИ КЛИHИЧЕСКИХ И ЛАБОРАТОРНЫХ ИССЛЕДОВАНИЯХ'
        elif ds[d] == 'ТРАВМЫ,ОТРАВЛЕH.И HЕКОТОР.ДРУГИЕ ПОСЛЕД.ВОЗДЕЙСТВ.ВHЕШH.ПРИЧИH':
            ds[d] = 'ТРАВМЫ, ОТРАВЛЕНИЯ И НЕКОТОРЫЕ ДРУГИЕ ПОСЛЕДСТВИЯ ВОЗДЕЙСТВИЯ ВНЕШНИХ ПРИЧИН'
        disease_id = diseases[ds[d]]
        result['disease_id'] = disease_id
        for year in years:
            result['year'] = int(year)
            for row in range(3, child_sheet.nrows-2):
                r = child_sheet.row_values(row)
                if r[1] == "Базарнокарабулакский" or r[1] == "Б.КАРАБУЛАКСКИЙ" or r[1] == 'БАЗАРHО-КАРАБУЛ. РАЙОH':
                    r[1] = "Базарно-Карабулакский"
                elif r[1] == 'БАЛТАЙСКИЙ Р-ОH':
                    r[1] = 'Балтайский'
                elif r[1] == 'ВОСКРЕСЕHСКИЙ Р-ОH':
                    r[1] = 'Воскресенский'
                elif r[1] == "Энгельсский" or r[1] == "ЭНГЕЛЬС + pайон" or r[1] == 'ЭHГЕЛЬС(+РАЙОH)':
                    r[1] = "Энгельский"
                elif r[1] == "Ровенский" or r[1] == "РОВЕНСКИЙ" or r[1] == 'РОВЕHСКИЙ Р-ОH':
                    r[1] = "Ровновский"
                elif r[1] == "АЛ.ГАЙСКИЙ" or r[1] == 'АЛ.ГАЙСКИЙ РАЙОH':
                    r[1] = "Александрово-Гайский"
                elif r[1] == 'АРКАДАКСКИЙ РАЙОH':
                    r[1] = "Аркадакский"
                elif r[1] == "ОЗИНКИНСКИЙ":
                    r[1] = "Озинский"
                elif r[1] == "ТАТИЩЕВСКИЙ+п.Светлый":
                    r[1] = "Татищевский"
                elif r[1] == "АТКАРСК":
                    r[1] = "Аткарский"
                elif r[1] == "БАЛАКОВО(+район)" or r[1] == 'БАЛАКОВО(+РАЙОH)':
                    r[1] = "Балаковский"
                elif r[1] == "БАЛАШОВ + pайон" or r[1] == 'БАЛАШОВ(+РАЙОH)':
                    r[1] = "Балашовский"
                elif r[1] == "ВОЛЬСК+район+Шиханы" or r[1] == 'ВОЛЬСК(+РАЙОH)':
                    r[1] = "Вольский"
                elif r[1] == "КРАСНОАРМЕЙСК" or r[1] == 'КРАСHОАРМЕЙСК':
                    r[1] = "Красноармейский"
                elif r[1] == "МАРКС":
                    r[1] = "Марксовский"
                elif r[1] == "САРАТОВ":
                    r[1] = "г.Саратов"
                elif r[1] == "ХВАЛЫНСК" or r[1] == 'ХВАЛЫHСК':
                    r[1] = "Хвалынский"
                elif r[1] == 'РОМАHОВСКИЙ РАЙОH':
                    r[1] = 'Романовский'
                elif r[1] == 'п.Светлый':
                    # Sad trombone
                    continue

                if r[1].strip() != 'САРАТОВ (ГОР)':
                    try:
                        district_id = districts.index(
                            r[1].title().strip() + " район") + 1
                    except ValueError:
                        try:
                            district_id = districts.index(
                                r[1].title().strip().replace('h', 'н').replace('H', 'Н') + " район") + 1
                        except ValueError:
                            district_id = districts.index(
                                r[1].title().strip().replace('h',
                                                             'н').replace('Р-Он',
                                                                          'район').replace('H', 'Н')) + 1
                else:
                    district_id = 3
                result["district_id"] = district_id

                if not isinstance(child_sheet.row_values(row)[2:][years.index(year) * disease_id], str):
                    result['children'] = child_sheet.row_values(row)[2:][years.index(year) * disease_id]
                else:
                    result['children'] = 0

                if not isinstance(teen_sheet.row_values(row)[2:][years.index(year) * disease_id], str):
                    result['teenagers'] = teen_sheet.row_values(row)[2:][years.index(year) * disease_id]
                else:
                    result['teenagers'] = 0

                if not isinstance(adult_sheet.row_values(row)[2:][years.index(year) * disease_id], str):
                    result['adults'] = adult_sheet.row_values(row)[2:][years.index(year) * disease_id]
                else:
                    result['adults'] = 0

                if not models.Year.query.filter_by(year=result["year"]).first():
                    db.session.add(models.Year(year=result["year"]))
                    db.session.commit()

                result["year_id"] = models.Year.query.filter_by(
                    year=result["year"]).first().id
                # del i["year"]
                db.session.add(models.DiseasePopulation(**result))
        db.session.commit()


if __name__ == "__main__":
    all_districts = list(map(str,
                             models.District.query.order_by(models.District.id).all()))
    all_diseases = dict()
    for x in models.Disease.query.order_by(models.Disease.id).all():
        all_diseases[x.name] = x.id
    print(parse_diseases(sys.argv[1], all_districts, all_diseases))