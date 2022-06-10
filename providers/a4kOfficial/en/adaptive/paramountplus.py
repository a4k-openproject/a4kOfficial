# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import re

from providerModules.a4kOfficial.core import Core


class sources(Core):
    def __init__(self):
        super(sources, self).__init__()
        self._providers = ['pmp']
        self._scheme = "standard_web"
        self._movie_url = "plugin://{}/?_=play&id={}"
        self._episode_url = "plugin://{}/?_=play&id={}"

    def _get_service_id(self, item):
        offers = item["offers"]
        service_offers = [
            o for o in offers if o['package_short_name'] in self._providers
        ]
        if not service_offers:
            return None

        offer = service_offers[0]
        url = offer['urls'][self._scheme]
        id = (
            url.split('?')[0].split('/')[-1]
            if item['object_type'] == 'movie'
            else re.findall('/video/(.+?)/', url)[0]
        )

        return id
