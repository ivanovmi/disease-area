from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    coordinates = db.Column(db.String(120), unique=True, nullable=True)

    def __init__ (self, name, coordinates=None):
        self.name = name
        self.coordinates = coordinates

    def __repr__ (self):
        return self.name

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    address = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(120), unique=True, nullable=True)
    coordinates = db.Column(db.String(120), nullable=True)

    district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    district = db.relationship('District',
            backref=db.backref('hospitals', lazy='dynamic', uselist=True))

    def __init__ (self, name, district, address=None, phone=None, coordinates=None):
        self.name = name
        self.district = district
        self.address = address
        self.phone = phone
        self.coordinates = coordinates

    def __repr__ (self):
        return self.name

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)

    year = db.Column(db.Integer, nullable=True)
    children = db.Column(db.Integer, nullable=True)
    children_observed = db.Column(db.Integer, nullable=True)
    adults = db.Column(db.Integer, nullable=True)
    adults_observed = db.Column(db.Integer, nullable=True)

    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    hospitals = db.relationship('Hospital',
            backref=db.backref('diseases', lazy='dynamic', uselist=True))

    def __init__ (self, name, hospitals, year, adults=0, adults_observed=0,
            children=0, children_observed=0):
        self.name = name
        self.hospitals = hospitals
        self.year = int(year)
        self.children = int(children)
        self.children_observed = int(children_observed)
        self.adults = int(adults)
        self.adults_observed = int(adults_observed)
        self.all = self.children + self.adults
        self.all_observer = self.children_observed + self.adults_observed

    def __repr__ (self):
        return '{0}{1}'.format(self.name,self.year)

class Population(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    all = db.Column(db.Integer)
    adults = db.Column(db.Integer)
    children = db.Column(db.Integer)
    employable = db.Column(db.Integer)
    employable_men = db.Column(db.Integer)
    employable_women = db.Column(db.Integer)

    district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    district = db.relationship('District',
            backref=db.backref('population', lazy='dynamic', uselist=True))

    def __init__ (self, year, district,
            men=0, women=0, children=0, employable_men=0, employable_women=0):

        self.district = district
        self.year = int(year)
        self.men = int(men)
        self.women = int(women)
        self.all = self.men + self.women
        self.children = int(children)
        self.employable_men = int(employable_men)
        self.employable_women = int(employable_women)
        self.adults = int(self.all - self.children)
        self.employable = int(self.employable_men + self.employable_women)

    def __repr__ (self):
        return '{}:{}'.format(self.year, self.all)
