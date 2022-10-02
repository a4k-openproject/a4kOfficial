# -*- coding: utf-8 -*-
from . import adaptive
from . import direct


def get_torrent():
    return []


def get_hosters():
    return []


def get_adaptive():
    return adaptive.__all__


def get_direct():
    return direct.__all__
