from __future__ import absolute_import, division, print_function, unicode_literals

import mock

import mopidy.config as config

import tornado.testing
import tornado.web
import tornado.websocket

from mopidy_weblibrary import Extension
from mopidy_weblibrary.web import StaticHandler


class BaseTest(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        extension = Extension()
        self.config = config.Proxy({'weblibrary': {
            'enabled': True
            }
        })
        return tornado.web.Application(extension.factory(self.config, mock.Mock()))


class StaticFileHandlerTest(BaseTest):

    def test_static_handler(self):
        response = self.fetch('/vendors/mopidy/mopidy.js', method='GET')

        assert response.code == 200

    def test_get_version(self):
        assert StaticHandler.get_version(None, None) == Extension.version


class RedirectHandlerTest(BaseTest):

    def test_redirect_handler(self):
        response = self.fetch('/', method='GET', follow_redirects=False)

        assert response.code == 301
        response.headers['Location'].endswith('index.html')


class IndexHandlerTestMusicBox(BaseTest):

    def test_index_handler(self):
        response = self.fetch('/index.html', method='GET')
        assert response.code == 200

    def test_get_title_musicbox(self):
        response = self.fetch('/index.html', method='GET')
        body = tornado.escape.to_unicode(response.body)

        assert '<title>WebLibrary</title>' in body


class IndexHandlerTestMopidy(BaseTest):

    def get_app(self):
        extension = Extension()
        self.config = config.Proxy({'weblibrary': {
            'enabled': True
            }
        })
        return tornado.web.Application(extension.factory(self.config, mock.Mock()))

    def test_get_title_mopidy(self):
        response = self.fetch('/index.html', method='GET')
        body = tornado.escape.to_unicode(response.body)

        assert '<title>WebLibrary</title>' in body
