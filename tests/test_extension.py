from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

import mock

from mopidy_weblibrary import Extension


class ExtensionTests(unittest.TestCase):

    def test_get_default_config(self):
        ext = Extension()

        config = ext.get_default_config()

        assert '[weblibrary]' in config
        assert 'enabled = true' in config

    def test_get_config_schema(self):
        ext = Extension()

        schema = ext.get_config_schema()

        assert schema is not None

    def test_setup(self):
        registry = mock.Mock()

        ext = Extension()
        ext.setup(registry)
        calls = [mock.call('http:app', {'name': ext.ext_name, 'factory': ext.factory})]
        registry.add.assert_has_calls(calls, any_order=True)
