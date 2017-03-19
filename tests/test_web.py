from __future__ import absolute_import, division, print_function, unicode_literals

import mock

import mopidy.config as config

import tornado.testing
import tornado.web
import tornado.websocket

from mopidy_weblibrary import Extension


class BaseTest(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        extension = Extension()
        self.config = config.Proxy({'weblibrary': {
            'enabled': True
            }
        })
        return tornado.web.Application(extension.factory(self.config, mock.Mock()))


class IndexHandlerTest(BaseTest):

    def get_app(self):
        extension = Extension()
        self.config = config.Proxy({'weblibrary': {
            'enabled': True
            }
        })
        return tornado.web.Application(extension.factory(self.config, mock.Mock()))

    def test_get_title_mopidy(self):
        response = self.fetch('/', method='GET')
        body = tornado.escape.to_unicode(response.body)

        assert '<title>WebLibrary</title>' in body
