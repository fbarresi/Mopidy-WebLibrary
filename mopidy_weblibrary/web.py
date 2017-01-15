from __future__ import absolute_import, division, print_function, unicode_literals


import logging
import os

import tornado.web

import mopidy_weblibrary.webclient as mmw

logger = logging.getLogger(__name__)


class StaticHandler(tornado.web.StaticFileHandler):

    def get(self, path, *args, **kwargs):
        version = self.get_argument('v', None)
        if version:
            logger.debug('Get static resource for %s?v=%s', path, version)
        else:
            logger.debug('Get static resource for %s', path)
        return super(StaticHandler, self).get(path, *args, **kwargs)

    @classmethod
    def get_version(cls, settings, path):
        return mmw.Extension.version


class IndexHandler(tornado.web.RequestHandler):

    def initialize(self, config, path):
        self.__path = path
        self.__title = "WebLibrary"

    def get(self, path=""):
        return self.render("index.html", title=self.__title, templates=get_javascript_templates())

    def get_template_path(self):
        return self.__path


def get_javascript_templates():
    return """
        <!-- The template to display files available for upload -->
        <script id="template-upload" type="text/x-tmpl">
        {% for (var i=0, file; file=o.files[i]; i++) { %}
            <tr class="template-upload fade">
                <td>
                    <span class="preview"></span>
                </td>
                <td>
                    <p class="name">{%=file.name%}</p>
                    <strong class="error text-danger"></strong>
                </td>
                <td>
                    <p class="size">Processing...</p>
                    <div class="progress progress-striped active" role="progressbar" aria-valuemin="0"
                    aria-valuemax="100" aria-valuenow="0"><div class="progress-bar progress-bar-success"
                    style="width:0%;"></div></div>
                </td>
                <td>
                    {% if (!i && !o.options.autoUpload) { %}
                        <button class="btn btn-primary start" disabled>
                            <i class="glyphicon glyphicon-upload"></i>
                            <span>Start</span>
                        </button>
                    {% } %}
                    {% if (!i) { %}
                        <button class="btn btn-warning cancel">
                            <i class="glyphicon glyphicon-ban-circle"></i>
                            <span>Cancel</span>
                        </button>
                    {% } %}
                </td>
            </tr>
        {% } %}
        </script>
        <!-- The template to display files available for download -->
        <script id="template-download" type="text/x-tmpl">
        {% for (var i=0, file; file=o.files[i]; i++) { %}
            <tr class="template-download fade">
                <td>
                    <span class="preview">
                        {% if (file.thumbnailUrl) { %}
                            <a href="{%=file.url%}" title="{%=file.name%}" download="{%=file.name%}" data-gallery>
                            <img src="{%=file.thumbnailUrl%}"></a>
                        {% } %}
                    </span>
                </td>
                <td>
                    <p class="name">
                        {% if (file.url) { %}
                            <a href="{%=file.url%}" title="{%=file.name%}" download="{%=file.name%}"
                            {%=file.thumbnailUrl?'data-gallery':''%}>{%=file.name%}</a>
                        {% } else { %}
                            <span>{%=file.name%}</span>
                        {% } %}
                    </p>
                    {% if (file.error) { %}
                        <div><span class="label label-danger">Error</span> {%=file.error%}</div>
                    {% } %}
                </td>
                <td>
                    <span class="size">{%=o.formatFileSize(file.size)%}</span>
                </td>
                <td>
                    {% if (file.deleteUrl) { %}
                        <button class="btn btn-danger delete" data-type="{%=file.deleteType%}"
                        data-url="{%=file.deleteUrl%}"{% if (file.deleteWithCredentials) { %}
                        data-xhr-fields='{"withCredentials":true}'{% } %}>
                            <i class="glyphicon glyphicon-trash"></i>
                            <span>Delete</span>
                        </button>
                        <input type="checkbox" name="delete" value="1" class="toggle">
                    {% } else { %}
                        <button class="btn btn-warning cancel">
                            <i class="glyphicon glyphicon-ban-circle"></i>
                            <span>Cancel</span>
                        </button>
                    {% } %}
                </td>
            </tr>
        {% } %}
        </script>
        """


class UploadHandler(tornado.web.RequestHandler):

    def initialize(self, config):

        webclient = mmw.Webclient(config)

        self.__can_upload = webclient.has_upload_path()

    def post(self):
        messages = []
        try:
            if self.can_upload():
                subpath = self.get_argument('subpath', '')
                if not subpath.endswith(os.path.sep):
                    subpath += os.path.sep
                if subpath.startswith(os.path.sep):
                    subpath = subpath[1:]

                if not os.path.exists(self.get_upload_path()+subpath):
                    messages.append("subdirectory " + subpath + " not exists, it will be created")
                    os.makedirs(self.get_upload_path()+subpath)
                absolute_path = self.get_upload_path()+subpath

                for key in self.request.files:
                    for file in self.request.files[key]:
                        original_fname = file['filename']

                        output_file = open(absolute_path + original_fname, 'wb')
                        output_file.write(file['body'])
                        logger.info("Uploaded file: " + absolute_path + original_fname)
                        messages.append("file " + original_fname + " was uploaded")
            else:
                messages.append("cannot upload... ;( ")
        except Exception as e:
            logger.error('Error during uploading music', exception=e)
            messages.append('An error has occurred! Please retry.')
        variables_dict = {
            'can_upload': self.can_upload(),
            'upload_path': self.__upload_path,
            'has_messages': True,
            'messages': messages
        }

        return variables_dict

    def get_upload_path(self):
        return self.__upload_path

    def can_upload(self):
        return self.__can_upload


class FilesHandler(tornado.web.RequestHandler):

    def initialize(self, config):
        self.__initialized = True

    def get(self, path):
        return self.__initialized

    def delete(self, path):
        return self.__initialized
