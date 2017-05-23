# models.py
from sys import path
from os.path import dirname as dir

path.append(dir(path[0]))

#from web.app import db
from app import db

class District(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    coordinates = db.Column(db.String(60000), nullable=True)

    def __init__(self, name, coordinates=None):
        self.name = name
        self.coordinates = coordinates

    def __repr__(self):
        return self.name


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_of = db.Column(db.String(120), nullable=True)
    name = db.Column(db.String(120), unique=True)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    doctor = db.Column(db.String(120), nullable=True)
    site = db.Column(db.String(120), nullable=True)
    info = db.Column(db.String(1000), nullable=True)
    coordinates = db.Column(db.String(120), nullable=True)

    district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    district = db.relationship('District',
                               backref=db.backref('hospitals', lazy='dynamic',
                                                  uselist=True))

    def __init__(self, name, district, address=None, phone=None, coordinates=None):
        self.name = name
        self.district = district
        self.address = address
        self.phone = phone
        self.coordinates = coordinates

    def __repr__(self):
        return self.name


class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description


class DiseasePopulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=True)
    children = db.Column(db.Integer, nullable=True)
    children_observed = db.Column(db.Integer, nullable=True)
    adults = db.Column(db.Integer, nullable=True)
    adults_observed = db.Column(db.Integer, nullable=True)

    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    hospital = db.relationship('Hospital',
                               backref=db.backref('population', lazy='dynamic',
                                                  uselist=True))

    disease_id = db.Column(db.Integer, db.ForeignKey('disease.id'))
    disease = db.relationship('Disease',
                              backref=db.backref('population', lazy='dynamic',
                                                 uselist=True))

    def __init__(self, disease, hospital, year, adults=0, adults_observed=0,
                 children=0, children_observed=0):
        self.disease = disease
        self.hospital = hospital
        self.year = int(year) if year else 0
        self.children = int(children)
        self.children_observed = int(children_observed)
        self.adults = int(adults)
        self.adults_observed = int(adults_observed)
        self.all = self.children + self.adults
        self.all_observed = self.children_observed + self.adults_observed

    def __repr__(self):
        return '{0}{1}'.format(self.name, self.year)


class Population(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    all = db.Column(db.Integer)
    men = db.Column(db.Integer)
    women = db.Column(db.Integer)
    children = db.Column(db.Integer)
    teenagers = db.Column(db.Integer)
    adults = db.Column(db.Integer)
    employable = db.Column(db.Integer)
    country_population = db.Column(db.Integer)
    district_id = db.Column(db.Integer, db.ForeignKey('district.id'))
    district = db.relationship('District',
                               backref=db.backref('population', lazy='dynamic',
                                                  uselist=True))


class Year(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)


class HospitalType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(120), nullable=True)


class Ages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age_border = db.Column(db.String(120),nullable=True)


class Reprod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer)
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    borned = db.Column(db.Integer)
    died = db.Column(db.Integer)
    nat_add = db.Column(db.Integer)


class Nathality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer)
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    _15_17 = db.Column(db.Integer)
    _18_24 = db.Column(db.Integer)
    _25_29 = db.Column(db.Integer)
    _30_34 = db.Column(db.Integer)
    _35_older = db.Column(db.Integer)


class Morthality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer)
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    died_under_1 = db.Column(db.Integer)
    all_population = db.Column(db.Integer)
    city_population = db.Column(db.Integer)
    village_population = db.Column(db.Integer)


class Migration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer)
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    added = db.Column(db.Integer)
    substituded = db.Column(db.Integer)
    diff = db.Column(db.Integer)


class SocialDiseases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer)
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    disease_id = db.Column(db.Integer, db.ForeignKey("disease.id"))
    morbidity = db.Column(db.Integer)
    prevalence = db.Column(db.Integer)


class Marriage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer)
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    marriage = db.Column(db.Integer)
    divorce = db.Column(db.Integer)


class Personal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer)
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    docs_on_10000 = db.Column(db.Integer)
    nurse_on_10000 = db.Column(db.Integer)


class Berth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year_id = db.Column(db.Integer)
    district_id = db.Column(db.Integer, db.ForeignKey("district.id"))
    berth_year = db.Column(db.Integer)
    berth_hospital_year = db.Column(db.Integer)
    berth_dispensery_year = db.Column(db.Integer)
    berth_days = db.Column(db.Integer)
    berth_hospitals_days = db.Column(db.Integer)
    berth_dispensery_days = db.Column(db.Integer)


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120))
    type = db.Column(db.String(15))
