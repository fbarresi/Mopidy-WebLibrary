from __future__ import absolute_import, division, print_function, unicode_literals
import json
import logging
import tornado.web
import re
import urllib
import mopidy_weblibrary.webclient as mmw

logger = logging.getLogger(__name__)

MIN_FILE_SIZE = 1  # bytes
MAX_FILE_SIZE = 999000  # bytes
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

    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small'
        elif file['size'] > MAX_FILE_SIZE:
            file['error'] = 'File is too big'
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
        file.seek(0, 2)  # Seek to the end of the file
        size = file.tell()  # Get the position of EOF
        file.seek(0)  # Reset the file position to the beginning
        return size

    def write_blob(self, data, info):
        try:
            if info['path'] == '':
                return None
            key = info['path'].encode('utf-8') + info['name'].encode('utf-8')
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
                        result['url'] = self.request.host_url + '/files/' + key
                        result['deleteUrl'] = result['url']
                        result['deleteType'] = 'DELETE'
                    else:
                        result['error'] = 'Failed to store uploaded file.'
                results.append(result)
        return results

    def post(self):
        if self.request.get('_method') == 'DELETE':
            return self.delete()
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

    def initialize(self, config):
        self.__initialized = True

    def get(self, path):
        return self.__initialized

    def delete(self, path):
        return self.__initialized
