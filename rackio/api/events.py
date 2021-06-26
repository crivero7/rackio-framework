# -*- coding: utf-8 -*-
"""rackio/api/events.py

This module implements all class Resources for Events.
"""

import json
from datetime import datetime

from rackio import status_code

from .core import RackioResource
from .auth_hook import auth_token

from ..dao import EventsDAO
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE
from ..managers.auth import GUEST_ROLE


class BaseResource(RackioResource):
    
    dao = EventsDAO()


class EventCollectionResource(BaseResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE, GUEST_ROLE])
    def on_get(self, req, resp):

        doc = self.dao.get_all()

        resp.body = json.dumps(doc, ensure_ascii=False)

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE])
    def on_post(self, req, resp):
        
        user = req.media.get('user')
        message = req.media.get('message')
        description = req.media.get('description')
        priority = req.media.get('priority')
        criticity = req.media.get('criticity')
        
        doc = self.dao.write(user, message, description, priority, criticity)

        resp.body = json.dumps(doc, ensure_ascii=False)
        resp.status = status_code.HTTP_200
    