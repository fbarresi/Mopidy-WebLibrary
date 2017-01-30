from __future__ import unicode_literals

import os

from mopidy import config, ext

__version__ = '1.0.0'


class Extension(ext.Extension):

    dist_name = 'Mopidy-WebLibrary'
    ext_name = 'weblibrary'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        return schema

    def setup(self, registry):
        registry.add(
            'http:app', {'name': self.ext_name, 'factory': self.factory})

    def factory(self, config, core):
        from tornado.web import RedirectHandler
        from .web import IndexHandler, UploadHandler, FilesHandler, StaticHandler
        path = os.path.join(os.path.dirname(__file__), 'static')
        return [
            (r'/upload', UploadHandler),
            (r'/files', FilesHandler),
            (r'/', RedirectHandler, {'url': 'index.html'}),
            (r'/(index.html)', IndexHandler, {'config': config, 'path': path}),
            (r'/(.*)', StaticHandler, {'path': path})

        ]
