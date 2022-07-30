# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from . import adaptive, direct


def get_torrent():
    return []


def get_hosters():
    return []


def get_adaptive():
    return adaptive.__all__


def get_direct():
    return direct.__all__
