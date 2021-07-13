# -*- coding: utf-8 -*-
"""rackio/dbmodels.py

This module implements classes for
modelling the trending process.
"""
from datetime import datetime, date
from io import BytesIO

from peewee import Proxy, Model, CharField, TextField, DateField, DateTimeField
from peewee import  IntegerField, FloatField, BlobField, ForeignKeyField, BooleanField

proxy = Proxy()

SQLITE = 'sqlite'
MYSQL = 'mysql'
POSTGRESQL = 'postgresql'


class BaseModel(Model):
    class Meta:
        database = proxy


class TagTrend(BaseModel):

    name = CharField()
    start = DateTimeField()
    period = FloatField()


class TagValue(BaseModel):

    tag = ForeignKeyField(TagTrend, backref='values')
    value = FloatField()
    timestamp = DateTimeField(default=datetime.now)


class Event(BaseModel):

    user = CharField()
    message = TextField()
    description = TextField()
    classification = TextField()
    priority = IntegerField(default=0)
    criticity = IntegerField(default=0)
    date_time = DateTimeField()


class Alarm(BaseModel):
    
    user = CharField()
    message = TextField()
    description = TextField()
    classification = TextField()
    priority = IntegerField(default=0)
    date_time = DateTimeField()
    name = TextField()
    state = TextField()


class AlarmSummary(BaseModel):
    
    name = TextField()
    state = TextField()
    alarm_time = DateTimeField()
    ack_time = DateTimeField(null=True)
    description = TextField()
    classification = TextField()
    priority = IntegerField(default=0)
    

class Blob(BaseModel):

    name = CharField()
    blob = BlobField()

    @classmethod
    def get_value(cls, blob_name):

        blob = Blob.select().where(Blob.name==blob_name).get()
        blob = BytesIO(blob.blob)

        blob.seek(0)

        return blob.getvalue()


class UserRole(BaseModel):

    role = CharField()


class User(BaseModel):

    username = TextField(unique=True)
    password = TextField()
    role = ForeignKeyField(UserRole, backref='user')

    @staticmethod
    def verify_username(username):
        
        try:
            User.get(User.username==username)
            return True

        except:

            return False


class Authentication(BaseModel):

    user = ForeignKeyField(User)
    key = TextField()

    expire = DateField(default=date.today)


class Anomaly(BaseModel):

    user = CharField()
    instrument = TextField()
    anomaly = TextField()
    date_time = DateTimeField()


class System(BaseModel):

    system_name = TextField(unique=True)

    @classmethod
    def add(cls, system_name):
        r"""
        Create a new record in the Systems table
        """
        system = System.create(system_name=system_name)

        return system


class Reliability(BaseModel):

    timestamp = DateTimeField(default=datetime.now)
    leak = BooleanField(default=False)
    false_leak = BooleanField(default=False)
    no_detected_leak = BooleanField(default=False)
    system = ForeignKeyField(System)
    user = ForeignKeyField(User)

    @classmethod
    def add(cls, username, system_name, leak=False, false_leak=False, no_detected_leak=False):
        r"""
        Create a new record in the Reliability table
        """
        user = User.get(username=username)
        system = System.get(system_name=system_name)

        return Reliability.create(
            user_id=user.id, 
            system_id=system.id,
            leak=leak,
            false_leak=false_leak,
            no_detected_leak=no_detected_leak
            )

    @classmethod
    def add_leak(cls, username, system_name, leak=True, false_leak=False, no_detected_leak=False):
        r"""
        Create a new record in the Reliability table
        """
        user = User.get(username=username)
        system = System.get(system_name=system_name)

        return Reliability.create(
            user_id=user.id, 
            system_id=system.id,
            leak=leak,
            false_leak=false_leak,
            no_detected_leak=no_detected_leak
            )

    @classmethod
    def add_false_leak(cls, username, system_name, leak=True, false_leak=True, no_detected_leak=False):
        r"""
        Create a new record in the Reliability table
        """
        user = User.get(username=username)
        system = System.get(system_name=system_name)

        return Reliability.create(
            user_id=user.id, 
            system_id=system.id,
            leak=leak,
            false_leak=false_leak,
            no_detected_leak=no_detected_leak
            )

    @classmethod
    def add_no_detected_leak(cls, username, system_name, leak=True, false_leak=False, no_detected_leak=True):
        r"""
        Create a new record in the Reliability table
        """
        user = User.get(username=username)
        system = System.get(system_name=system_name)

        return Reliability.create(
            user_id=user.id, 
            system_id=system.id,
            leak=leak,
            false_leak=false_leak,
            no_detected_leak=no_detected_leak
            )

    @classmethod
    def get_leak(cls, system_name, start, stop):
        r"""
        Documentation here
        """
        system = System.get(system_name=system_name)
        how_many_leaks = len(Reliability.select().where(
            (Reliability.timestamp >= start) &
            (Reliability.timestamp <= stop) &
            (Reliability.leak == True) &
            (Reliability.system == system.id)))

        return how_many_leaks

    @classmethod
    def get_false_leak(cls, system_name, start, stop):
        r"""
        Documentation here
        """
        system = System.get(system_name=system_name)
        how_many_false_leaks = len(Reliability.select().where(
            (Reliability.timestamp >= start) &
            (Reliability.timestamp <= stop) &
            (Reliability.false_leak == True) &
            (Reliability.system == system.id)))

        return how_many_false_leaks

    @classmethod
    def get_no_detected_leak(cls, system_name, start, stop):
        r"""
        Documentation here
        """

        system = System.get(system_name=system_name)
        how_many_no_detected_leaks = len(Reliability.select().where(
                    (Reliability.timestamp >= start) &
                    (Reliability.timestamp <= stop) &
                    (Reliability.no_detected_leak == True) &
                    (Reliability.system == system.id)))

        return how_many_no_detected_leaks
