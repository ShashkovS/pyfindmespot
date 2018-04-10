class ReverseProxied(object):
    """This middleware can be applied to add HTTP proxy support to an application
    which access the WSGI environment directly.
    It sets `REMOTE_ADDR`, `HTTP_HOST`, `wsgi.url_scheme` from `X-Forwarded` headers.
    Also front-end server can be configured to quietly bind this to a URL other than /
    and to an HTTP scheme that is different than what is used locally.

    In nginx:
    location /myprefix/ {
        proxy_set_header X-Script-Name /myprefix;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
    }

    So app will be accessible
    locally at http://localhost:5001/myapp
    externally at https://example.com/myprefix/myapp
    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme

        remote_addr = environ.get('HTTP_X_FORWARDED_FOR', '')
        if remote_addr:
            environ['REMOTE_ADDR'] = remote_addr

        forwarded_host = environ.get('HTTP_X_FORWARDED_HOST', '')
        if forwarded_host:
            environ['HTTP_HOST'] = forwarded_host

        return self.app(environ, start_response)
