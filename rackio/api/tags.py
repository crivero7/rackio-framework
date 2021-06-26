# -*- coding: utf-8 -*-
"""rackio/api/tags.py

This module implements all Tag Resources for the Tag Engine.
"""

import json

from .core import RackioResource
from .auth_hook import auth_token

from ..dao import TagsDAO
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE
from ..managers.auth import GUEST_ROLE


class BaseResource(RackioResource):

    dao = TagsDAO()
    

class TagCollectionResource(BaseResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE, GUEST_ROLE])
    def on_get(self, req, resp):

        doc = self.dao.get_all()

        resp.body = json.dumps(doc, ensure_ascii=False)


class TagResource(BaseResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE])
    def on_get(self, req, resp, tag_id):

        doc = self.dao.get(tag_id)

        resp.body = json.dumps(doc, ensure_ascii=False)

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE])
    def on_post(self, req, resp, tag_id):
        
        value = req.media.get('value')

        _cvt = self.tag_engine
        _type = _cvt.read_type(tag_id)

        if not "." in tag_id:
            if _type == "float":
                value = float(value)
            elif _type == "int":
                value = int(value)
            elif _type == "str":
                value = str(value)
            elif _type == "bool":
                if value == "true":
                    value = True
                elif value == "false":
                    value = False
                else:
                    value = bool(value)

        result = self.dao.write(tag_id, value)

        if result["result"]:

            doc = {
                'result': True
            }

        else:

            doc = {
                'result': False
            }
        
        resp.body = json.dumps(doc, ensure_ascii=False)
        