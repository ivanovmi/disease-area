import pprint
import json

js = {
    "container": "testA",
    "view": "tree",
    "activeTitle": True,
    "data": [
        {"id": "1", "open": True, "value": "The Shawshank Redemption", "data": [
            {"id": "1.1", "value": "Part 1"},
            {"id": "1.2", "value": "Part 2"},
            {"id": "1.3", "value": "Part 3"}
        ]},
        {"id": "2", "value": "The Godfather", "data": [
            {"id": "2.1", "value": "Part 1"},
            {"id": "2.2", "value": "Part 2"}
        ]}
    ]
}


def generate_json(div_id="gmap-menu", markers=[], polygons=[]):
    json_template = {"container": div_id,
                     "view": "tree",
                     "activeTitle": True,
                     "template": "{common.icon()} {common.checkbox()} #value#",
                     "threeState": True,
                     "data": [],
                     "ready": "function(){this.openAll();}"}

    idx = 1
    for m in markers:
        json_template["data"].append({
            "id": str(idx),
            "value": m["name"]
        })

    pprint.pprint(json_template)





if __name__ == '__main__':
    a = [{'lat': '51.50',
          'name': 'Государственное автономное учреждение здравоохранения «Энгельсская городская больница № 2»',
          'infobox': "Государственное автономное учреждение здравоохранения «Энгельсская городская больница № 2»<br><b>Адрес:</b> 413124 Саратов.обл.,г.Энгельс, ул.Полиграфическая,д.1<br><a href=http://enggb2.medportal.saratov.gov.ru/ target='_blank'>Сайт учреждения</a>",
          'icon': '//maps.google.com/mapfiles/ms/icons/red-dot.png',
          'lng': '46.15'},
         {'lat': '51.47',
          'name': 'Государственное автономное учреждение здравоохранения «Энгельсская городская клиническая больница № 1»',
          'infobox': "Государственное автономное учреждение здравоохранения «Энгельсская городская клиническая больница № 1»<br><b>Адрес:</b> 413116, Саратовская область, г.Энгельс, ул. Весенняя ,6<br><a href=http://enggb1.medportal.saratov.gov.ru/ target='_blank'>Сайт учреждения</a>",
          'icon': '//maps.google.com/mapfiles/ms/icons/red-dot.png',
          'lng': '46.15'},
         {'lat': '51.45',
          'name': 'Государственное автономное учреждение здравоохранения Саратовской области «Энгельсская районная больница»',
          'infobox': "Государственное автономное учреждение здравоохранения Саратовской области «Энгельсская районная больница»<br><b>Адрес:</b> г. Энгельс, Волжский пр-т, 61<br><a href=http://engerb.medportal.saratov.gov.ru/ target='_blank'>Сайт учреждения</a>",
          'icon': '//maps.google.com/mapfiles/ms/icons/red-dot.png',
          'lng': '46.08'},
         {'lat': '51.59',
          'name': 'Государственное учреждение здравоохранения «Областная клиническая больница»',
          'infobox': "Государственное учреждение здравоохранения «Областная клиническая больница»<br><b>Адрес:</b> 410053 г.Саратов, Смирновское ущелье, д.1<br><a href=http://okb.medportal.saratov.gov.ru/ target='_blank'>Сайт учреждения</a>",
          'icon': '//maps.google.com/mapfiles/ms/icons/red-dot.png',
          'lng': '45.96'}]
    b = [{'stroke_weight': 3,
          'stroke_color': '#0AB0DE',
          'fill_opacity': 0.5,
          'stroke_opacity': 1.0,
          'name': 'Александрово-Гайский район',
          'fill_color': '#ABC321'},
         {'stroke_weight': 3,
          'stroke_color': '#0AB0DE',
          'fill_opacity': 0.5,
          'stroke_opacity': 1.0,
          'name': 'Аткарский район',
          'fill_color': '#ABC321'},
         {'stroke_weight': 3,
          'stroke_color': '#0AB0DE',
          'fill_opacity': 0.5,
          'stroke_opacity': 1.0,
          'name': 'Базарно-Карабулакский район',
          'fill_color': '#ABC321'}]

    generate_json(markers=a)
