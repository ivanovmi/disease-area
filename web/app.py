from sys import path
from os.path import dirname as dir_

path.append(dir_(path[0]))

import ast
import logging
import forms
import functools
from collections import OrderedDict
import json
import pprint
import os

from config import Config
from flask import Flask
from flask import abort, request, render_template, redirect, session, url_for

from werkzeug.utils import secure_filename

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
db.init_app(app)

UPLOAD_FOLDER = 'static/downloads/'
os.makedirs(UPLOAD_FOLDER, mode=0o775, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from models import *
import xls_parser

with app.test_request_context():
    db.create_all()

console = logging.StreamHandler()
log = logging.getLogger("app")
log.addHandler(console)
log.setLevel(logging.DEBUG)

admin_navigation = ['district', 'disease', 'population', 'hospital',
                    'disease population']

navigation = ['markers_map', 'disease_map', 'population_map']

style = "height:530px;width:870px;margin:0;"



@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if (form.validate_on_submit() and
            form.username.data == app.config['ADMIN_USERNAME'] and
            form.password.data == app.config['ADMIN_PASSWORD']):
        session['username'] = form.username.data
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/logout/')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get('username', None)
        if username != 'admin':
            abort(401)
            #redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


color = {1: '4b9c3d',
         2: '0e29a6',
         3: '46dcac',
         4: 'c0a6e1',
         5: '10e4e8',
         6: 'ab3463',
         7: 'f0fe09',
         8: 'd7f195',
         9: '406ed4',
         10: '7037cb',
         11: 'c8c069',
         12: '34e73a',
         13: 'ac3929',
         14: 'b5cc93',
         15: 'e4861f',
         16: 'f13ebe',
         17: 'a8e610',
         18: '138c7c',
         19: '37508c',
         20: 'f94c15',
         21: '00d010',
         22: 'f2dc77',
         23: 'f1a0d3',
         24: '419ef4',
         25: '503bed',
         26: '70361b',
         27: '0a3d6e',
         28: 'b7110f',
         29: 'c6f50e',
         30: 'c165b0',
         31: 'd03f27',
         32: 'afc760',
         33: 'd4a57a',
         34: 'ecbc62',
         35: '366737',
         36: '65ebdb',
         37: 'a2a3ec',
         38: '2f61a6',
         39: 'd1f703'
         }


@app.route('/markers_map', methods=['GET', 'POST'])
def markers_map():
    if request.method == 'POST':
        log.debug(request.form)
        _json = dict()
        _json['types'] = request.form.get('types').split(',')
        _json['district'] = request.form.get('district')
        return redirect(url_for('markers_map')+'?{}'.format(_json))

    markers = _get_markers()
    _json = request.args

    try:
        _json = next(iter(_json))
    except StopIteration:
        _json = None

    try:
        _json = ast.literal_eval(_json)
    except ValueError:
        _json = None

    log.debug(_json)
    mrkrs = list()
    if _json is not None:
        if _json['district'] != '0':
            markers[:] = [d for d in markers if
                          str(d.get('district')) == _json['district']]
        if _json['types'] != ['']:
            for marker in markers:
                remove = True
                for _type in _json['types']:
                    if _type in marker['types']:
                        remove = False
                if not remove:
                    mrkrs.append(marker)
        else:
            mrkrs = markers

    districts = _get_all_districts()
    districts.append(District(name='--'))
    return render_template('markers_map.html', navigation=navigation,
                           mark=mrkrs, dist=districts, colors=color)


@app.route('/disease_map', methods=["GET", "POST"])
def disease_map():
    if request.method == "POST":
        log.debug(request.form)
        _json = dict()
        _json['year_id'] = request.form.get('year')
        if request.form.get('header') == 'Первичная':
            key = 'first'
        elif request.form.get('header') == 'Общая':
            key = 'all'
        _json['column'] = request.form.get(key.lower())
        _json['key'] = key
        _json['age'] = request.form.get('age')
        return redirect(url_for('disease_map')+'?{}'.format(_json))

    _json = request.args
    criteria = dict()
    dataset = dict()

    years = {
        'first': [_get_year_by_id(x) for x in list(set([x.year_id for x in DiseasePopulation.query.order_by(DiseasePopulation.is_first).all() if x.is_first == 1]))],
        'all': [_get_year_by_id(x) for x in list(set([x.year_id for x in DiseasePopulation.query.order_by(DiseasePopulation.is_first).all() if x.is_first == 0]))]
    }

    try:
        _json = next(iter(_json))
    except StopIteration:
        _json = None

    try:
        _json = ast.literal_eval(_json)
    except ValueError:
        _json = None

    log.debug(_json)

    cr = dict()
    if _json is not None:
        query = 'DiseasePopulation.query.filter_by(disease_id={}, is_first={}, year_id={}).all()'.format(_json['column'], 1 if _json['key'] == 'first' else 0, _json['year_id'])
        res = eval(query)

        for i in res:
            if int(_json['age']) == 1:
                log.debug('children')
                criteria[i.district_id] = i.children
                cr[_get_district_by_id(i.district_id)] = round(i.children, 2)
                dataset['age'] = 'дети'
            elif int(_json['age']) == 2:
                log.debug('teens')
                criteria[i.district_id] = i.teenagers
                cr[_get_district_by_id(i.district_id)] = round(i.teenagers, 2)
                dataset['age'] = 'подростки'
            elif int(_json['age']) == 3:
                log.debug('adult')
                criteria[i.district_id] = i.adults
                cr[_get_district_by_id(i.district_id)] = round(i.adults, 2)
                dataset['age'] = 'взрослые'
            elif int(_json['age']) == 4:
                log.debug('all')
                criteria[i.district_id] = i.children + i.teenagers + i.adults
                cr[_get_district_by_id(i.district_id)] = round(i.children + i.teenagers + i.adults, 2)
                dataset['age'] = 'общий показатель'

        dataset['label'] = '{}'.format(_get_disease_by_id(_json['column']).name)
        dataset['year'] = '{}'.format(_get_year_by_id(_json['year_id']).year)

    cr = list(cr.items())
    dataset['cr'] = cr

    if criteria != {}:
        polygons, legend = _get_polygons(criteria)
    else:
        polygons = legend = {}

    diseases = _get_all_diseases()
    return render_template('disease_map.html', navigation=navigation, legend=legend,
                           poly=polygons, years=years, diseases=diseases, dataset=dataset)


@app.route('/population_map', methods=["GET", "POST"])
def population_map():
    if request.method == "POST":
        log.debug(request.form)
        _json = dict()
        _json['year_id'] = request.form.get('year')
        if request.form.get('header') == 'Браки':
            key = 'Marriage'
        elif request.form.get('header') == "Численность":
            key = 'Population'
        elif request.form.get('header') == "Рождаемость":
            key = 'Nathality'
        elif request.form.get('header') == "Смертность":
            key = 'Morthality'
        elif request.form.get('header') == "Воспроизводство":
            key = 'Reprod'
        elif request.form.get('header') == "Миграция":
            key = 'Migration'
        _json['column'] = request.form.get(key.lower())
        _json['key'] = key
        return redirect(url_for('population_map')+'?{}'.format(_json))

    _json = request.args
    criteria = dict()
    dataset = dict()
    years = {
        'Population': [_get_year_by_id(x) for x in list(set([x.year_id for x in
                                                            Population.query.order_by(
                                                                Population.year_id).all()]))],
        'Nathality': [_get_year_by_id(x) for x in list(set([x.year_id for x in
                                                            Nathality.query.order_by(
                                                                Nathality.year_id).all()]))],
        'Morthality': [_get_year_by_id(x) for x in list(set([x.year_id for x in
                                                             Morthality.query.order_by(
                                                                 Morthality.year_id).all()]))],
        'Reprod': [_get_year_by_id(x) for x in list(set(
            [x.year_id for x in Reprod.query.order_by(Reprod.year_id).all()]))],
        'Marriage': [_get_year_by_id(x) for x in list(set([x.year_id for x in
                                                           Marriage.query.order_by(
                                                               Marriage.year_id).all()]))],
        'Migration': [_get_year_by_id(x) for x in list(set([x.year_id for x in
                                                            Migration.query.order_by(
                                                                Migration.year_id).all()]))]
    }

    try:
        _json = next(iter(_json))
    except StopIteration:
        _json = None

    try:
        _json = ast.literal_eval(_json)
    except ValueError:
        _json = None

    log.debug(_json)
    mapping = {
        'Population': {
            "1": "all",
            "2": "men",
            "3": "women",
            "4": "children",
            "5": "teenagers",
            "6": "adults",
            "7": "employable",
            "8": "country_population"
        },
        'Nathality': {
            "1": "_15_17",
            "2": "_18_24",
            "3": "_25_29",
            "4": "_30_34",
            "5": "_35_older"
        },
        'Morthality': {
            "1": "all_population",
            "2": "city_population",
            "3": "village_population",
            "4": "died_under_1"
        },
        'Reprod': {
            "1": "borned",
            "2": "died",
            "3": "nat_add"
        },
        'Marriage': {
            '1': 'marriage',
            '2': 'divorce'
        },
        'Migration': {
            "1": "added",
            "2": "substituded",
            "3": "diff"
        }
    }

    cr = dict()
    if _json is not None:
        query = '{}.query.order_by({}.id).all()'.format(_json['key'], _json['key'])
        res = eval(query)
        for i in res:
            criteria[i.district_id] = eval('i.{}'.format(mapping[_json['key']][_json['column']]))
            cr[_get_district_by_id(i.district_id)] = eval('i.{}'.format(mapping[_json['key']][_json['column']]))

        dataset['label'] = mapping[_json['key']][_json['column']]
        dataset['labels'] = years[_json['key']]
        dataset['data'] = []
        dataset['year'] = _get_year_by_id(_json['year_id']).year

        for year in years[_json['key']]:
            query = '{}.query.filter_by(year_id={}).all()'.format(_json['key'],
                                                                  year.id)
            res = eval(query)
            data = [eval('x.{}'.format(mapping[_json['key']][_json['column']])) for x in res]
            dataset['data'].append(round(sum(data)/len(res)))
            dataset['min'] = min(data)
            dataset['max'] = max(data)

    cr = list(cr.items())
    dataset['cr'] = cr

    log.debug(dataset)

    if criteria != {}:
        polygons, legend = _get_polygons(criteria)
    else:
        polygons = legend = {}

    log.debug(years)

    return render_template('population_map.html', navigation=navigation, legend=legend,
                           years=years, poly=polygons, dataset=dataset)


@app.route('/analysis')
def analysis():
    return render_template('analysis.html', navigation=navigation)


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('markers_map'))


@app.route('/district', methods=['GET', 'POST'])
@admin_required
def district():
    if request.method == 'POST':
        log.debug(request.form)
        name = request.form.get('name')
        coordinates = request.form.get('coordinates')

        district = District.query.filter_by(name=name).first()
        if name and not district:
            db.session.add(District(name=name, coordinates=coordinates))
            db.session.commit()
        return redirect(url_for('district'))

    return render_template('district.html', districts=_get_all_districts(),
                           navigation=navigation,
                           admin_navigation=admin_navigation)


@app.route('/district/delete', methods=['POST'])
@admin_required
def district_delete():
    if request.method == 'POST':
        district_id = int(request.form.get('district_id'))
        log.debug(request.form)
        district = District.query.filter_by(id=district_id).first()

        log.debug(district)

        if district and not district.hospitals.count() \
                and not district.population.count():
            db.session.delete(district)
            db.session.commit()

    return redirect(url_for('district'))


@app.route('/disease', methods=['GET', 'POST'])
@admin_required
def disease():
    """
    Для отобажения формы с болезнями
    """
    if request.method == 'POST':
        log.debug(request.form)
        name = request.form.get('name')
        if name:
            db.session.add(Disease(name=name))
            db.session.commit()
    return render_template('disease.html', diseases=_get_all_diseases(),
                           navigation=navigation, admin_navigation=admin_navigation)


@app.route('/disease/delete', methods=['POST'])
@admin_required
def disease_delete():
    """
    Для удаления болезни из списка
    """
    if request.method == 'POST':
        disease_id = int(request.form.get('disease_id'))
        log.debug(request.form)
        disease = Disease.query.filter_by(id=disease_id).first()

        if disease and not disease.population.count():
            db.session.delete(disease)
            db.session.commit()

    return redirect(url_for('disease'))


@app.route('/hospital', methods=['GET', 'POST'])
@admin_required
def hospital():
    """
    Для отображения формы с больницами
    """
    if request.method == 'POST':
        log.debug(request.form)
        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        coordinates = request.form.get('coordinates')
        district_id = request.form.get('district_id')

        district = District.query.filter_by(id=district_id).first() if district_id else None

        if name and district:
            db.session.add(Hospital(name=name, address=address, phone=phone,
                                    coordinates=coordinates, district=district))
            db.session.commit()

    return render_template('hospital.html', hospitals=_get_all_hospitals(),
                           districts=_get_all_districts(),
                           navigation=navigation, admin_navigation=admin_navigation)


@app.route('/hospital/delete', methods=['POST'])
@admin_required
def hospital_delete():
    """
    Для удаления больницы из списка
    """
    if request.method == 'POST':
        hospital_id = int(request.form.get('hospital_id'))
        log.debug(request.form)
        hospital = Hospital.query.filter_by(id=hospital_id).first()
        if hospital and not hospital.population.count():
            db.session.delete(hospital)
            db.session.commit()

    return redirect(url_for('hospital'))


@app.route('/population', methods=['GET', 'POST'])
@admin_required
def population():
    """
    Для отображения форм с населением
    """
    if request.method == 'POST':
        if request.form.get('year'):
            year = request.form.get('year')
            men = request.form.get('men')
            women = request.form.get('women')
            children = request.form.get('children')
            employable_men = request.form.get('employable_men')
            employable_women = request.form.get('employable_women')
            district_id = request.form.get('district_id')
            district = _get_district_by_id(district_id)
            if year and district:
                db.session.add(Population(district=district,
                                          year=year,
                                          men=men,
                                          women=women,
                                          children=children,
                                          employable_men=employable_men,
                                          employable_women=employable_women
                                          )
                               )
                db.session.commit()
        elif request.files:
            all_districts = list(map(str, District.query.order_by(District.id).all()))
            log.debug(request.files)
            if request.files.get('reprod_file'):
                type = 'reprod'
                f = request.files['reprod_file']
                filename = f.filename
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    secure_filename(f.filename)))
                reprod = xls_parser.parse_reprod(
                    os.path.join(app.config['UPLOAD_FOLDER'],
                                 secure_filename(f.filename)),
                    all_districts)

                for i in reprod:
                    add_new_year(year=i["year"])

                    i["year_id"] = Year.query.filter_by(
                        year=i["year"]).first().id
                    del i["year"]
                    db.session.add(Reprod(**i))
            elif request.files.get('marriage_file'):
                type = 'marriage'
                f = request.files['marriage_file']
                filename = f.filename
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    secure_filename(f.filename)))

                marriage = xls_parser.parse_marriage(
                    os.path.join(app.config['UPLOAD_FOLDER'],
                                 secure_filename(f.filename)),
                    all_districts)

                for i in marriage:
                    add_new_year(year=i["year"])

                    i["year_id"] = Year.query.filter_by(year=i["year"]).first().id
                    del i["year"]
                    db.session.add(Marriage(**i))
            elif request.files.get('migration_file'):
                type = 'migration'
                f = request.files['migration_file']
                filename = f.filename
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    secure_filename(f.filename)))

                migration = xls_parser.parse_migration(
                    os.path.join(app.config['UPLOAD_FOLDER'],
                                 secure_filename(f.filename)),
                    all_districts)

                for i in migration:
                    add_new_year(year=i["year"])

                    i["year_id"] = Year.query.filter_by(
                        year=i["year"]).first().id
                    del i["year"]
                    db.session.add(Migration(**i))

            elif request.files.get('mortality_file'):
                type = 'mortality'
                f = request.files['mortality_file']
                filename = f.filename
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    secure_filename(f.filename)))

                mortality = xls_parser.parse_mortality(
                    os.path.join(app.config['UPLOAD_FOLDER'],
                                 secure_filename(f.filename)),
                    all_districts)

                for i in mortality:
                    add_new_year(year=i["year"])

                    i["year_id"] = Year.query.filter_by(
                        year=i["year"]).first().id
                    del i["year"]
                    db.session.add(Morthality(**i))
            elif request.files.get('nathality_file'):
                type = 'nathality'
                f = request.files['nathality_file']
                filename = f.filename
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    secure_filename(f.filename)))

                nathality = xls_parser.parse_nathality(
                    os.path.join(app.config['UPLOAD_FOLDER'],
                                 secure_filename(f.filename)),
                    all_districts)

                for i in nathality:
                    add_new_year(year=i["year"])

                    i["year_id"] = Year.query.filter_by(
                        year=i["year"]).first().id
                    del i["year"]
                    db.session.add(Nathality(**i))
            elif request.files.get('population_file'):
                type = 'population'
                f = request.files['population_file']
                filename = f.filename
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    secure_filename(f.filename)))

                popul = xls_parser.parse_population(
                    os.path.join(app.config['UPLOAD_FOLDER'],
                                 secure_filename(f.filename)),
                    all_districts)
                for i in popul:
                    log.debug(i['year'])
                    add_new_year(year=i["year"])

                    i["year_id"] = Year.query.filter_by(
                        year=i["year"]).first().id
                    del i["year"]

                    db.session.add(Population(**i))

            db.session.add(Files(filename=filename,
                                 type=type))
            db.session.commit()

    return render_template('population.html', populations=_get_all_population(),
                           districts=_get_all_districts(), files=_get_files(), years=_get_all_years(),
                           navigation=navigation, admin_navigation=admin_navigation)


@app.route('/population/delete', methods=['POST'])
@admin_required
def population_delete():
    """
    Для удаления населения из списка
    """
    if request.method == 'POST':
        population_id = int(request.form.get('population_id'))
        log.debug(request.form)
        population = Population.query.filter_by(id=population_id).first()
        if population:
            db.session.delete(population)
            db.session.commit()

    return redirect(url_for('population'))


@app.route('/disease_population', methods=['GET', 'POST'])
@admin_required
def disease_population():
    if request.method == 'POST':
        log.debug(request.form)

        if request.files:
            all_districts = list(map(str, District.query.order_by(District.id).all()))
            all_diseases = dict()
            for x in Disease.query.order_by(Disease.id).all():
                all_diseases[x.name] = x.id
            log.debug(request.files)
            if request.files.get('dp_file'):
                f = request.files['dp_file']
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    secure_filename(f.filename)))
                xls_parser.parse_diseases(
                    os.path.join(app.config['UPLOAD_FOLDER'],
                                 secure_filename(f.filename)),
                    all_districts, all_diseases, db)

            return redirect(url_for('disease_population'))

    return render_template('disease_population.html',
                           disease_populations=_get_all_disease_population(),
                           diseases=_get_all_diseases(),
                           hospitals=_get_all_hospitals(),
                           navigation=navigation, admin_navigation=admin_navigation)


@app.route('/disease_population/delete', methods=['POST'])
@admin_required
def disease_population_delete():
    if request.method == 'POST':
        log.debug(request.form)
        disease_population_id = request.form.get('disease_population_id')
        disease_population = DiseasePopulation.query.filter_by(
            id=disease_population_id).first()
        if disease_population:
            db.session.delete(disease_population)
            db.session.commit()

    return redirect(url_for('disease_population'))


def add_new_year(year):
    if not Year.query.filter_by(year=year).first():
        log.debug("Adding new year to db")
        db.session.add(Year(year=year))
        db.session.commit()


def _get_all_population():
    """
    Для получения всего населения
    :return: list, состоящий из словарей
    """
    return Population.query.order_by(Population.year).all()


def _get_all_districts():
    """
    Для получения всех районов
    :return: list, состоящий из словарей
    """
    return District.query.order_by(District.name).all()


def _get_all_diseases():
    """
    Для получения всех болезней
    :return: list, состоящий из словарей
    """
    return Disease.query.order_by(Disease.name).all()


def _get_all_hospitals():
    """
    Для получения всех больниц
    :return: list, состоящий из словарей
    """
    return Hospital.query.order_by(Hospital.name).all()


def _get_all_disease_population():
    return DiseasePopulation.query.order_by(DiseasePopulation.year).all()


def _get_disease_by_id(disease_id):
    return Disease.query.filter_by(
        id=disease_id).first() if disease_id else None


def _get_hospital_by_id(hospital_id):
    return Hospital.query.filter_by(
        id=hospital_id).first() if hospital_id else None


def _get_district_by_id(district_id):
    """
    Для получения всех районов по идентификатору
    :return: dict
    """
    return District.query.filter_by(id=district_id).first() if district_id else None


def _get_year_by_id(year_id):
    """
    Для получения всех районов по идентификатору
    :return: dict
    """
    return Year.query.filter_by(id=year_id).first() if year_id else None


def _get_all_years():
    return Year.query.order_by(Year.id).all()


def _get_files():
    return Files.query.order_by(Files.id).all()


def _get_markers():
    """
    Для составления маркеров на карте
    :return: list, состоящий из словарей
    """
    markers = []
    hospitals = _get_all_hospitals()
    for hospital in hospitals:
        h = dict()
        # Получаем долготу(lng) и широту(lat)
        h['lng'], h['lat'] = hospital.coordinates.split('; ')
        h['infobox'] = ("{}<br><b>Адрес:</b> {}"
                        "<br><b>Телефон:</b> {}"
                        "<br><b>ФИО главного врача:</b> {}"
                        "<br><a href={} target='_blank'>Сайт учреждения</a>"
                        "<br><b>Доп. информация:</b> {}".format(hospital.name,
                                                                hospital.address,
                                                                hospital.phone,
                                                                hospital.doctor,
                                                                hospital.site,
                                                                hospital.info))
        h['name'] = hospital.name
        h['district'] = hospital.district_id
        h['types'] = hospital.type_of.split(',')
        markers.append(h)
    return markers


def _get_selected_markers():
    markers = []
    hospitals = _get_all_hospitals()
    for hospital in hospitals:
        h = dict()
        # Получаем долготу(lng) и широту(lat)
        h['lng'], h['lat'] = hospital.coordinates.split('; ')
        h['infobox'] = ("{}<br><b>Адрес:</b> {}"
                        "<br><b>Телефон:</b> {}"
                        "<br><b>ФИО главного врача:</b> {}"
                        "<br><a href={} target='_blank'>Сайт учреждения</a>"
                        "<br><b>Доп. информация:</b> {}".format(hospital.name,
                                                                hospital.address,
                                                                hospital.phone,
                                                                hospital.doctor,
                                                                hospital.site,
                                                                hospital.info))
        h['name'] = hospital.name
        markers.append(h)
    return markers

red_heat_map = """FFE6E6
FFD8D8
FFC5C5
FFB0B0
FF9A9A
FF9A9A
FF6868
FF4949
FE2C2C
FF1212
CB3333
A62929
7B1818"""


def _get_polygons(criteria):
    polygons = []
    districts = _get_all_districts()
    map_colors = dict()
    legend = OrderedDict()
    h = red_heat_map.split('\n')
    log.debug(criteria)
    _s = sorted(criteria, key=criteria.get)

    for i in range(0, len(_s), 3):
        legend[h[int(i/3)]] = "{}  {}".format(int(round(criteria[_s[i]], 0)), int(round(criteria[_s[i+2]], 0)))
        map_colors[_s[i]], map_colors[_s[i+1]], map_colors[_s[i+2]] = h[int(i/3)], h[int(i/3)], h[int(i/3)]
    log.debug(legend)

    for district in districts:
        pol = {
            'stroke_color': '#0AB0DE',
            'stroke_opacity': 1.0,
            'stroke_weight': 3,
            'fill_color': map_colors[district.id],
            'fill_opacity': .5,
            'path': [],
            'name': district.name
        }
        coord = ast.literal_eval(district.coordinates)
        for c in coord:
            pol['path'].append([c[1], c[0]])

        polygons.append(pol)

    return polygons, legend


if __name__ == '__main__':
    from os import path
    import os

    extra_dirs = ['static', 'templates']
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in os.walk(extra_dir):
            for filename in files:
                filename = path.join(dirname, filename)
                if path.isfile(filename):
                    extra_files.append(filename)
    app.run(host='0.0.0.0', extra_files=extra_files, debug=True,
            port=int(os.environ.get('PORT', 5000)))
