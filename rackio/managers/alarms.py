# -*- coding: utf-8 -*-
"""rackio/managers/alarms.py

This module implements Alarm Manager.
"""
from datetime import datetime
import queue

from ..engine import CVTEngine
from ..models import TagObserver
from ..alarms import SHELVED, USER
from ..dbmodels import Alarm as AlarmModel
from ..dao import EventsDAO




class AlarmManager:

    dao = EventsDAO()

    def __init__(self):

        self._alarms = list()
        self._tag_queue = queue.Queue()

    def get_queue(self):

        return self._tag_queue
    
    def append_alarm(self, alarm):

        self._alarms.append(alarm)

    def get_alarm(self, name):

        for _alarm in self._alarms:
            if name == _alarm.get_name():
                return _alarm

        return

    def get_alarm_by_tag(self, tag):

        for _alarm in self._alarms:
            if tag == _alarm.get_tag():
                return _alarm

        return

    def get_alarms(self):

        result = list()

        for _alarm in self._alarms:
            result.append(_alarm)

        return result

    def alarm_tags(self):

        result = [_alarm.get_tag() for _alarm in self._alarms]

        return tuple(result)

    def summary(self):

        result = dict()

        alarms = [_alarm.get_name() for _alarm in self._alarms]
        
        result["length"] = len(alarms)
        result["alarms"] = alarms
        result["tags"] = self.alarm_tags()

        return result

    def attach_all(self):

        _cvt = CVTEngine()

        def attach_observers(entity):

            _tag = entity.get_tag()

            observer = TagObserver(self._tag_queue)
            query = dict()
            query["action"] = "attach"
            query["parameters"] = {
                "name": _tag,
                "observer": observer,
            }

            _cvt.request(query)
            _cvt.response()

        for _alarm in self._alarms:

            attach_observers(_alarm)

    def execute(self, tag):

        _cvt = CVTEngine()
        value = _cvt.read_tag(tag)

        for _alarm in self._alarms:

            if _alarm.get_state() == SHELVED:

                _now = datetime.now()
                
                if _alarm._shelved_until:

                    if _now >= _alarm._shelved_until:
                        message = "Alarm {} unshelved".format(_alarm.get_name())
                        priority = 2
                        classification = USER
                        AlarmModel.create(
                            user=USER, 
                            message=message,
                            description=_alarm._description,
                            classification=classification, 
                            priority=priority, 
                            date_time=_now,
                            name=_alarm.get_name(),
                            state=_alarm.get_state()
                        )

                        criticity = 2
                        
                        self.dao.write(USER, message, _alarm._description, priority, criticity)
                        
                        _alarm.unshelve()
                        continue

                    continue

                continue

            if tag == _alarm.get_tag():

                _alarm.update(value)

            

    