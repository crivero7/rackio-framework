# -*- coding: utf-8 -*-
"""rackio/api/trends.py

This module implements all Waveforms Resources.
"""

import json

from .core import RackioResource
from .auth_hook import auth_token

from ..dao import TagsDAO
from ..managers.auth import SYSTEM_ROLE, ADMIN_ROLE, GUEST_ROLE, OPERATOR_ROLE, ANALYST_ROLE
from ..managers.auth import SUPERVISOR_ROLE


class BaseResource(RackioResource):

    dao = TagsDAO()


class WaveformResource(BaseResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE, GUEST_ROLE])
    def on_post(self, req, resp, tag_id):

        tstart = req.media.get('tstart')
        tstop = req.media.get('tstop')

        doc = self.dao.get_waveform(tag_id, tstart, tstop)

        resp.body = json.dumps(doc, ensure_ascii=False)


class WaveformCollectionResource(BaseResource):

    @auth_token([SYSTEM_ROLE, ADMIN_ROLE, SUPERVISOR_ROLE, OPERATOR_ROLE, ANALYST_ROLE, GUEST_ROLE])
    def on_post(self, req, resp):

        tags = req.media.get('tags')

        tstart = req.media.get('tstart')
        tstop = req.media.get('tstop')
    
        result = self.dao.get_waveforms(tags, tstart, tstop)

        resp.body = json.dumps(result, ensure_ascii=False)