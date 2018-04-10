class ReverseProxied(object):
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
