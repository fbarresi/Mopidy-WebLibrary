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

    def get_media_dirs_config(self):
        dirs = list(self.config.get(u'file', {}).get(u'media_dirs', []))
        directories = []
        for d in dirs:
            directories.append(d.split("|")[0])
        return directories
