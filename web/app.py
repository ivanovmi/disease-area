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
from flask_googlemaps import GoogleMaps, Map, icons

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

admin_navigation = ['district', 'population', 'hospital', 'disease',
                    'disease population']

navigation = ['markers_map', 'disease_map', 'population_map', 'analysis']

style = "height:530px;width:870px;margin:0;"

GoogleMaps(app, key=app.config['GMAPS_KEY'])


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
            redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/markers_map', methods=['GET'])
def markers_map():
    markers = _get_markers()
    gmap = Map("disease_map",
               lat=51.35, lng=46.70,
               zoom=7, style=style,
               cluster=True, cluster_gridsize=10, markers=markers)
    #json_menu = json.dumps(generate_json(), ensure_ascii=False)
    return render_template('markers_map.html', navigation=navigation, gmap=gmap,
                           mark=markers)


@app.route('/disease_map')
def disease_map():
    polygons = _get_polygons()
    gmap = Map("disease_map",
               lat=51.35, lng=46.70,
               zoom=7, style=style,
               cluster=True, cluster_gridsize=10, polygons=polygons)
    return render_template('disease_map.html', navigation=navigation,
                           gmap=gmap, poly=polygons)


@app.route('/population_map')
def population_map():
    polygons = _get_polygons()
    gmap = Map("disease_map",
               lat=51.35, lng=46.70,
               zoom=7, style=style,
               cluster=True, cluster_gridsize=10, polygons=polygons)
    return render_template('population_map.html', navigation=navigation,
                           gmap=gmap, poly=polygons)


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
                           navigation=navigation)


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
                           navigation=navigation)


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
                           navigation=navigation)


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
                    db.session.add(Mortality(**i))
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
                    add_new_year(year=i["year"])

                    i["year_id"] = Year.query.filter_by(
                        year=i["year"]).first().id
                    del i["year"]
                    db.session.add(Population(**i))

            db.session.add(Files(filename=filename,
                                 type=type))
            db.session.commit()

    return render_template('population.html', populations=_get_all_population(),
                           districts=_get_all_districts(), files=_get_files(),
                           navigation=navigation)


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

        year = request.form.get('year')
        children = request.form.get('children')
        children_observed = request.form.get('children_observed')
        adults = request.form.get('adults')
        adults_observed = request.form.get('adults_observed')
        hospital_id = request.form.get('hospital_id')
        disease_id = request.form.get('disease_id')

        disease = _get_disease_by_id(disease_id)
        hospital = _get_hospital_by_id(hospital_id)

        if year and disease and hospital:
            db.session.add(DiseasePopulation(year=year,
                                             children=children,
                                             children_observed=children_observed,
                                             adults=adults,
                                             adults_observed=adults_observed,
                                             hospital=hospital,
                                             disease=disease,
                                             )
                           )
            db.session.commit()

    return render_template('disease_population.html',
                           disease_populations=_get_all_disease_population(),
                           diseases=_get_all_diseases(),
                           hospitals=_get_all_hospitals(),
                           navigation=navigation)


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
        h['icon'] = icons.dots.red
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


def _get_polygons():
    polygons = []
    districts = _get_all_districts()
    colors = "#ABC321"
    for district in districts:
        pol = {
            'stroke_color': '#0AB0DE',
            'stroke_opacity': 1.0,
            'stroke_weight': 3,
            'fill_color': colors,
            'fill_opacity': .5,
            'path': [],
            'name': district.name
        }
        coord = ast.literal_eval(district.coordinates)
        for c in coord:
            pol['path'].append({'lng': c[0], 'lat': c[1]})

        polygons.append(pol)

    return polygons


def generate_json(div_id="gmap-menu"):
    json_template = {"container": div_id,
                     "view": "tree",
                     "template": "{common.icon()} {common.checkbox()} #value#",
                     "threeState": True,
                     "data": [],
                     "ready": "function(){this.openAll();}"}

    _hospitals = _get_all_hospitals()
    _districts = _get_all_districts()
    districts = dict() #OrderedDict()

    for district in _districts:
        districts[district.name] = []

    for hospital in _hospitals:
        districts[hospital.district.name].append(hospital.name)

    id_base = 1
    for key, value in districts.items():
        if value != []:
            tmp = dict()
            tmp['id'] = str(id_base)
            tmp['value'] = key
            tmp['data'] = []
            id_sec = 1
            for el in value:
                sec_tmp = dict()
                sec_tmp['id'] = '{}.{}'.format(id_base, id_sec)
                sec_tmp['value'] = el
                tmp['data'].append(sec_tmp)
                id_sec += 1
            json_template['data'].append(tmp)
            id_base += 1
    with open('static/js/data.json', 'w') as js_file:
        json.dump(json_template['data'], js_file, ensure_ascii=False)

    return json_template

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
    app.run(host='0.0.0.0',extra_files=extra_files, debug=True)
