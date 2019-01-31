from datetime import datetime
from app import db, loginMgr
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import threading
import time
import math



@loginMgr.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    authenticated = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(150), unique=True)
    created_on = db.Column(db.DateTime,
                           server_default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           server_default=db.func.now(),
                           server_onupdate=db.func.now())
    isEnabled = db.Column(db.Boolean(), server_default='0')

    def __init__(self, email, plaintext_password):
        self.email = email
        self.password_hash = plaintext_password
        self.authenticated = False

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    def __init__(self, user_id, role_id):
        self.user_id = id
        self.role_id = Role

    def __repr__(self):
        return '<Role {} for User {}>'.format(self.user_id, self.role_id)


class UserAttributes(db.Model):
    __tablename__ = 'user_attr'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    strength = db.Column(db.Integer(), default=1)
    intelligence = db.Column(db.Integer(), default=1)
    endurance = db.Column(db.Integer(), default=1)
    totaldmg = db.Column(db.Integer(), default=0)

    def __init__(self, strength, intelligence, endurance, totaldmg):
        self.user_id = User.id
        self.strength = strength
        self.intelligence = intelligence
        self.endurance = endurance
        self.totaldmg = totaldmg

    def __repr__(self):
        return '<User Attributes {}>'.format(self.id)


class Regions(db.Model):
    __tablename__ = 'regions'
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    colour = db.Column(db.String(50))
    file = db.Column(db.String(200))

    def __init__(self, name, colour, file):
        self.name = name
        self.colour = colour
        self.file = file

    def __repr__(self):
        return '<Region {} Name {}>'.format(self.id, self.name)


class RegionAttributes(db.Model):
    __tablename__ = 'region_attributes'
    id = db.Column('regionId', db.Integer, primary_key=True)
    attack = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    hasBarracks = db.Column(db.Integer)
    hasHumanOwner = db.Column(db.Integer)
    isStartingRegion = db.Column(db.Integer)
    isoccupiedby = db.Column(db.String(50))

    def __init__(self, name, city, addr):
        self.attack = attack
        self.defense = defense
        self.hasBarracks = hasBarracks
        self.hasHumanOwner = hasHumanOwner
        self.isStartingRegion = isStartingRegion
        self.isoccupiedby = self.id

    def __repr__(self):
        return '<Region Attributes {}>'.format(self.id)


class CityAttributes(db.Model):
    __tablename__ = 'city_attr'
    id = db.Column('cityId', db.Integer, primary_key=True)
    name = db.Column(db.String)
    x = db.Column(db.Float)
    y = db.Column(db.Float)

    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __repr__(self):
        return '<City Attribute {}>'.format(self.name)


class SkillTracker(db.Model):
    __tablename__ = 'skilltracker'
    id = db.Column('upgradeid', db.Integer, primary_key=True, nullable=False, autoincrement=True)
    timesubmit = db.Column(db.Integer, nullable=False)
    timetowait = db.Column(db.Integer, nullable=False)
    timecomplete = db.Column(db.Integer, nullable=False)
    isactive = db.Column(db.Boolean, nullable=False, default=1)
    targetskill = db.Column(db.String, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    def __init__(self, userid, targetskill, currentlevel):
        self.userid = userid
        self.timesubmit = time.time()
        self.timetowait = 250 * math.sqrt(12)*(currentlevel)
        self.timecomplete = round(self.timesubmit+self.timetowait)
        self.targetskill = targetskill
        self.isactive = self.isactive

    def __repr__(self):
        return '<Skill Upgrade {}>'.format(self.id)


class SkillHistory(db.Model):
    __tablename__ = 'skillhistory'
    id = db.Column('upgradeid', db.Integer, primary_key=True, nullable=False, autoincrement=True)
    timesubmit = db.Column(db.Integer, nullable=False)
    timetowait = db.Column(db.Integer, nullable=False)
    timecomplete = db.Column(db.Integer, nullable=False)
    isactive = db.Column(db.Boolean, nullable=False, default=0)
    targetskill = db.Column(db.String, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    def __init__(self, userid, targetskill, timesubmit, timetowait, timecomplete):
        self.userid = userid
        self.timesubmit = timesubmit
        self.timetowait = timetowait
        self.timecomplete = timecomplete
        self.targetskill = targetskill
        self.isactive = self.isactive

    def __repr__(self):
        return '<Skill History {}>'.format(self.id)


class RegionWar(db.Model):
    __tablename__ = 'regionwar'
    id = db.Column(db.Integer, autoincrement=True, unique=True, primary_key=True)
    offdamage = db.Column(db.Integer)
    defdamage = db.Column(db.Integer)
    enddamage = db.Column(db.Integer)
    timesubmit = db.Column(db.Integer)
    regionida = db.Column(db.Integer, db.ForeignKey('regions.id'))
    regionidd = db.Column(db.Integer, db.ForeignKey('regions.id'))
    isactive = db.Column(db.Boolean)
    cityida = db.Column(db.Integer, db.ForeignKey('city_attr.cityId'))
    cityidd = db.Column(db.Integer, db.ForeignKey('city_attr.cityId'))

    def __init__(self, regiona, regiond, offdamage, defdamage, timesubmit=time.time()):
        self.id = self.id
        self.offdamage = offdamage
        self.defdamage = defdamage
        self.enddamage = abs(offdamage-defdamage)
        self.timesubmit = timesubmit
        self.regionida = regiona
        self.regionidd = regiond
        self.cityida = regiona
        self.cityidd = regiond
        self.isactive = 1

    def __repr__(self):
        return '<Region War {}>'.format(self.id)

class DamageWar(db.Model):
    __tablename__ = 'damagewar'
    id = db.Column(db.Integer, autoincrement=True, unique=True, primary_key=True)
    offordef = db.Column(db.String)
    damage = db.Column(db.Integer)
    timestamp = db.Column(db.Integer)
    userid = (db.Integer, db.ForeignKey('users.id'))

    def __init__(self, userid, offordef, damage):
        self.offordef = offordef
        self.damage = damage
        self.timestamp = time.time()
        self.userid = userid

    def __repr__(self):
        return '<War Damage {} at {} by {}>'.format(self.id, self.timestamp, self.userid)


class Articles(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, autoincrement=True, unique=True, primary_key=True)
    timesubmit = db.Column(db.Integer)
    timeupdate = db.Column(db.Float)
    title = db.Column(db.String)
    content = db.Column(db.String)
    user = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, content, user):
        self.content = content
        self.user = user
        timesubmit = time.time()

    def __repr__(self):
        return '<Atricle {}>'.format(self.id)