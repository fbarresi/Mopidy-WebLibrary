from __future__ import absolute_import, division, print_function, unicode_literals

import json
import logging
import os
import re
import sys
import urllib

from os.path import exists, isfile, join

import tornado.web

import mopidy_weblibrary.webclient as mmw

logger = logging.getLogger(__name__)

MIN_FILE_SIZE = 1  # bytes
MAX_FILE_SIZE = 102400000  # bytes
EXPIRATION_TIME = 300  # seconds
# If set to None, only allow redirects to the referer protocol+host.
# Set to a regexp for custom pattern matching against the redirect value:
REDIRECT_ALLOW_TARGET = None


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
        webclient = mmw.Webclient(config)
        self.__media_dirs = webclient.get_media_dirs_config()

    def get(self, template):
        path = self.get_argument('d', '')
        if not self.check_allowed_path(path):
            path = ''
        variables = {
            'templates': get_javascript_templates(),
            'upload_path': path,
            'tree': self.generate_current_tree(path),
        }
        return self.render(template, title=self.__title, **variables)

    def get_template_path(self):
        return self.__path

    def check_allowed_path(self, path):
        for d in self.__media_dirs:
            if path.startswith(d):
                return True
        return False

    def generate_current_tree(self, path):
        three = {'files': []}
        if path == '':
            for d in self.__media_dirs:
                three['files'].append({
                    'name': d,
                    'url': 'index.html?d='+d,
                    'deleteUrl': 'files?folder='+d,
                    'deleteType': 'DELETE'
                })
        else:
            three['files'].append({
                'name': '..',
                'url': 'index.html?d=' + os.path.dirname(path),
            })
            dirs = [f for f in os.listdir(path) if not isfile(join(path, f))]
            for d in dirs:
                folder_document = {
                    'name': d,
                    'url': 'index.html?d=' + join(path, d)
                }
                inner_files = os.listdir(join(path, d))
                if len(inner_files) == 0:
                    folder_document['deleteUrl'] = 'files?folder=' + join(path, d)
                    folder_document['deleteType'] = 'DELETE'
                three['files'].append(folder_document)
            three['files'].extend(self.generate_files_tree(path))
        return json.dumps(three)

    def generate_files_tree(self, path):
        files_list = []
        if path != '':
            files = [f for f in os.listdir(path) if isfile(join(path, f))]
            for fa in files:
                files_list.append({
                    'name': fa,
                    'url': 'files?file=' + join(path, fa),
                    'deleteUrl': 'files?file=' + join(path, fa),
                    'deleteType': 'DELETE'
                })
        return files_list


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

        <!-- The template to display files and folders -->
        <script id="template-tree" type="text/x-tmpl">
        {% for (var i=0, file; file=o.files[i]; i++) { %}
            <tr class="template-download fade in">
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
                            <a href="{%=file.url%}">{%=file.name%}</a>
                        {% } else { %}
                            <span>{%=file.name%}</span>
                        {% } %}
                    </p>
                    {% if (file.error) { %}
                        <div><span class="label label-danger">Error</span> {%=file.error%}</div>
                    {% } %}
                </td>
                <td>
                    <span class="size"></span>
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
                    {% } %}
                </td>
            </tr>
        {% } %}
        </script>
        """


class UploadHandler(tornado.web.RequestHandler):

    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
        elif file['path'] == '':
            file['error'] = 'No upload folder defined'
        else:
            return True
        return False

    def validate_redirect(self, redirect):
        if redirect:
            redirect_allow_target = ''
            if REDIRECT_ALLOW_TARGET:
                return REDIRECT_ALLOW_TARGET.match(redirect)
            referer = self.request.headers['referer']
            if referer:
                from urlparse import urlparse
                parts = urlparse(referer)
                redirect_allow_target = '^' + re.escape(
                    parts.scheme + '://' + parts.netloc + '/'
                )
            return re.match(redirect_allow_target, redirect)
        return False

    def get_file_size(self, file):
        return sys.getsizeof(file)

    def write_blob(self, data, info):
        try:
            if info['path'] == '':
                return None
            key = info['path'].encode('utf-8') + '/' + info['name'].encode('utf-8')
            output_file = open(key, 'wb')
            output_file.write(data)
            return key
        except Exception as e:
            logger.error('Error during uploading', exception=e)
            return None

    def handle_upload(self):
        results = []
        path = self.get_argument('path', '')
        for key in self.request.files:
            for file in self.request.files[key]:
                result = {}
                result['size'] = self.get_file_size(file['body'])
                result['path'] = path
                result['name'] = urllib.unquote(file['filename'])
                if self.validate(result):
                    key = self.write_blob(
                        file['body'],
                        result
                    )
                    if key is not None:
                        result['url'] = 'files?file=' + key
                        result['deleteUrl'] = result['url']
                        result['deleteType'] = 'DELETE'
                    else:
                        result['error'] = 'Failed to store uploaded file.'
                results.append(result)
        return results

    def post(self):
        result = {'files': self.handle_upload()}
        s = json.dumps(result)
        redirect = self.get_argument('redirect', '')
        if self.validate_redirect(redirect):
            return self.redirect(str(
                redirect.replace('%s', urllib.quote(s, ''), 1)
            ))
        if 'application/json' in self.request.headers.get('Accept'):
            self.add_header('Content-Type', 'application/json')
        self.write(s)


class FilesHandler(tornado.web.RequestHandler):

    def normalize(self, str):
        return urllib.quote(urllib.unquote(str), '')

    def get(self):
        file_name = self.get_argument('file')
        data = open(file_name, "rb")
        if data is None:
            return self.set_status(404)
        self.add_header('Content-Type', 'application/octet-stream')
        self.write(data.read())

    def post(self):
        path = self.get_argument('parent', '')
        folder_name = self.get_argument('name', '')
        if path is not '' and folder_name is not '':
            full_path = join(path, folder_name)
            if not exists(full_path):
                os.mkdir(full_path)
            return self.finish()
        return self.set_status(500)

    def delete(self):
        file_name = self.get_argument('file', '')
        if file_name != '':
            try:
                os.remove(file_name)
                result = {file_name.split('/')[-1]: True}
            except Exception as e:
                logger.error(e)
                self.set_status(500)
                result = {file_name.split('/')[-1]: False}
        else:
            folder = self.get_argument('folder', '')
            if folder != '':
                try:
                    os.rmdir(folder)
                    result = {folder.split('/')[-1]: True}
                except Exception as e:
                    logger.error(e)
                    self.set_status(500)
                    result = {folder.split('/')[-1]: False}

        if 'application/json' in self.request.headers.get('Accept'):
            self.add_header('Content-Type', 'application/json')
        s = json.dumps({'files': [result]})
        self.write(s)
