# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
from future.standard_library import install_aliases

install_aliases()

import xbmcdrm

from providerModules.a4kOfficial import common

WV_UUID = 'edef8ba9-79d6-4ace-a3c8-27dcd51d21ed'

WV_L1 = "L1"
WV_L2 = "L2"
WV_L3 = "L3"

FAKE_L1 = [
    "7011",
]


def get_widevine_level():
    wv_level = None

    if common.get_kodi_version(short=True) > 17:
        try:
            crypto = xbmcdrm.CryptoSession(WV_UUID, "AES/CBC/NoPadding", 'HmacSHA256')

            if not wv_level:
                wv_level = crypto.GetPropertyString('securityLevel')
                if wv_level:
                    wv_level = wv_level.upper()

                    try:
                        if wv_level == WV_L1:
                            system_id = crypto.GetPropertyString('systemId')
                            if system_id in FAKE_L1:
                                wv_level = WV_L3
                    except:
                        pass

        except Exception as e:
            common.log(
                "a4kOfficial: Failed detecting Widevine security level. {}".format(e)
            )

    if not wv_level:
        wv_level = WV_L3

    return wv_level or WV_L3
