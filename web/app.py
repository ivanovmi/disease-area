from sys import path
from os.path import dirname as dir

path.append(dir(path[0]))

import logging

from config import Config
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask_googlemaps import GoogleMaps, Map, icons

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
db.init_app(app)

from models import *

with app.test_request_context():
    db.create_all()

console = logging.StreamHandler()
log = logging.getLogger("app")
log.addHandler(console)
log.setLevel(logging.DEBUG)

navigation = ['district', 'population', 'hospital', 'disease']
GoogleMaps(app, key=app.config['GMAPS_KEY'])


def _get_markers():
    markers = []
    hospitals = _get_all_hospitals()
    for hospital in hospitals:
        #    'infobox': "Hello I am < b style='color:green;'>B< / b >!"
        h = {'icon': icons.dots.red}
        h['lat'], h['lng'] = hospital.coordinates.split('; ')
        h['infobox'] = "{}<br><b>Адрес:</b> {}<br><a href={} target='_blank'>Сайт учреждения</a>".format(hospital.name, hospital.address, hospital.phone)
        markers.append(h)
    return markers

@app.route('/', methods=['GET', 'POST'])
def index():
    markers = _get_markers()
    gmap = Map("disease_map",
               lat=51.50, lng=46.0,
               zoom=10, markers=markers,
               style="height:450px;width:1138px;margin:0;",
               cluster=True,
               cluster_gridsize=10)
    return render_template('index.html', navigation=navigation, gmap=gmap)


@app.route('/district', methods=['GET', 'POST'])
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
def district_delete():
    if request.method == 'POST':
        district_id = int(request.form.get('district_id'))
        log.debug(request.form)
        district = District.query.filter_by(id=district_id).first()

        log.debug(district)

        if district and not district.hospitals.count() and not district.population.count():
            db.session.delete(district)
            db.session.commit()

    return redirect(url_for('district'))


@app.route('/disease', methods=['GET', 'POST'])
def disease():
    if request.method == 'POST':
        log.debug(request.form)
        name = request.form.get('name')
        if name:
            db.session.add(Disease(name=name))
            db.session.commit()
    return render_template('disease.html', diseases=_get_all_diseases(),
                           navigation=navigation)


@app.route('/disease/delete', methods=['POST'])
def disease_delete():
    if request.method == 'POST':
        disease_id = int(request.form.get('disease_id'))
        log.debug(request.form)
        disease = Disease.query.filter_by(id=disease_id).first()

        if disease:
            db.session.delete(disease)
            db.session.commit()

    return redirect(url_for('disease'))


@app.route('/hospital', methods=['GET', 'POST'])
def hospital():
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
def hospital_delete():
    if request.method == 'POST':
        hospital_id = int(request.form.get('hospital_id'))
        log.debug(request.form)
        hospital = Hospital.query.filter_by(id=hospital_id).first()
        if hospital:
            db.session.delete(hospital)
            db.session.commit()

    return redirect(url_for('hospital'))


@app.route('/population', methods=['GET', 'POST'])
def population():
    if request.method == 'POST':
        log.debug(request.form)
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

    return render_template('population.html', populations=_get_all_population(),
                           districts=_get_all_districts(),
                           navigation=navigation)


@app.route('/population/delete', methods=['POST'])
def population_delete():
    if request.method == 'POST':
        population_id = int(request.form.get('population_id'))
        log.debug(request.form)
        population = Population.query.filter_by(id=population_id).first()
        if population:
            db.session.delete(population)
            db.session.commit()

    return redirect(url_for('population'))


def _get_all_population():
    return Population.query.order_by(Population.year).all()


def _get_all_districts():
    return District.query.order_by(District.name).all()


def _get_all_diseases():
    return Disease.query.order_by(Disease.name).all()


def _get_all_hospitals():
    return Hospital.query.order_by(Hospital.name).all()


def _get_district_by_id(district_id):
    return District.query.filter_by(id=district_id).first() if district_id else None


if __name__ == '__main__':
    app.run()
