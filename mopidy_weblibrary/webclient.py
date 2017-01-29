from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from mopidy_weblibrary import Extension

logger = logging.getLogger(__name__)


class Webclient(object):

    def __init__(self, config):
        self.config = config

    @property
    def ext_config(self):
        return self.config.get(Extension.ext_name, {})

    @classmethod
    def get_version(cls):
        return Extension.version

    @property
    def get_file_config(self):
        return self.config.get(u'file', {}).get(u'media_dirs', [])
