# -*- coding: utf-8 -*-
"""rackio/api/workers.py

This module implements all class Resources for Rackio Workers.
"""

import json

from rackio import status_code

from .core import RackioResource
from .auth_hook import auth_token

from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE
from ..managers.auth import GUEST_ROLE


class ContinousWorkerResource(RackioResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE, GUEST_ROLE])
    def on_get(self, req, resp, worker_name):

        app = self.get_app()
        manager = app.get_manager("alarm")

        alarm = manager.get_alarm(worker_name)

        if alarm:
            doc = alarm.serialize()

            resp.body = json.dumps(doc, ensure_ascii=False)

            resp.status = status_code.HTTP_200
        else:
            resp.status = status_code.HTTP_NOT_FOUND

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE, GUEST_ROLE])
    def on_post(self, req, resp, alarm_name):
        
        action = req.media.get('action')

        app = self.get_app()
        manager = app.get_manager("alarm")

        alarm = manager.get_alarm(alarm_name)

        if alarm:
            if action == "Acknowledge":

                alarm.acknowledge()

            doc = alarm.serialize()

            resp.body = json.dumps(doc, ensure_ascii=False)
            
            resp.status = status_code.HTTP_200
        else:
            resp.status = status_code.HTTP_NOT_FOUND
