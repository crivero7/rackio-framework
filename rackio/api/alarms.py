# -*- coding: utf-8 -*-
"""rackio/api/alarms.py

This module implements all class Resources for the Alarm Manager.
"""

import json

from rackio import status_code

from .core import RackioResource
from .auth_hook import auth_token

from ..dao import AlarmsDAO
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE
from ..managers.auth import GUEST_ROLE


class BaseResource(RackioResource):
    
    dao = AlarmsDAO()


class AlarmCollectionResource(BaseResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE, GUEST_ROLE])
    def on_get(self, req, resp):

        doc = self.dao.get_all()
        
        resp.body = json.dumps(doc, ensure_ascii=False)
 

class AlarmResource(BaseResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE, GUEST_ROLE])
    def on_get(self, req, resp, alarm_name):

        doc = self.dao.get(alarm_name)

        if doc:
            
            resp.body = json.dumps(doc, ensure_ascii=False)

        else:
            resp.status = status_code.HTTP_NOT_FOUND

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE])
    def on_post(self, req, resp, alarm_name):
        
        action = req.media.get('action')

        doc = self.dao.update(alarm_name, action)

        resp.body = json.dumps(doc, ensure_ascii=False)
            
            