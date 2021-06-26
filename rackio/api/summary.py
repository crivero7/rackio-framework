# -*- coding: utf-8 -*-
"""rackio/api/summary.py

This module implements all class Resources for the Alarm Manager.
"""

import json

from .core import RackioResource
from .auth_hook import auth_token

from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE
from ..managers.auth import GUEST_ROLE


class AppSummaryResource(RackioResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE, GUEST_ROLE])
    def on_get(self, req, resp):

        app = self.get_app()
        doc = app.summary()
        
        resp.body = json.dumps(doc, ensure_ascii=False)