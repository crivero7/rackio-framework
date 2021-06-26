# -*- coding: utf-8 -*-
"""rackio/api/history.py

This module implements History Resources.
"""

import json

from .core import RackioResource
from .auth_hook import auth_token

from ..dao import TagsDAO
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE


class BaseResource(RackioResource):

    dao = TagsDAO()


class TagHistoryResource(BaseResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE])
    def on_get(self, req, resp, tag_id):

        doc = self.dao.get_history(tag_id)

        resp.body = json.dumps(doc, ensure_ascii=False)
    