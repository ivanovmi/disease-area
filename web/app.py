# app.py
from sys import path
from os.path import dirname as dir

path.append(dir(path[0]))

import logging

from config import Config
from flask import Flask
from flask import request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import requests

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

navigation = ['district', 'hospital', 'disease']


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', navigation=navigation)


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

        if district and not district.hospitals.count():
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


def _get_all_districts():
    return District.query.order_by(District.name).all()


def _get_all_diseases():
    return Disease.query.order_by(Disease.name).all()


def _get_all_hospitals():
    return Hospital.query.order_by(Hospital.name).all()


def _get_coordinates(place):
    pass


if __name__ == '__main__':
    app.run()