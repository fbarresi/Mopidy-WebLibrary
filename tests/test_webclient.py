from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import mopidy.config as mopidy_config

from mopidy_weblibrary import Extension
from mopidy_weblibrary.webclient import Webclient


class WebclientTests(unittest.TestCase):

    def setUp(self):
        config = mopidy_config.Proxy(
            {
                'weblibrary': {
                    'enabled': True
                    }
            })

        self.ext = Extension()
        self.mmw = Webclient(config)

    def test_get_version(self):
        assert self.mmw.get_version() == self.ext.version
