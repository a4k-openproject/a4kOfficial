# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

from providerModules.a4kOfficial.core.library import LibraryCore


class sources(LibraryCore):
    def __init__(self):
        super(sources, self).__init__()
