from flask import Flask
from flask import jsonify
from flask import request
import werkzeug.contrib.fixers
import werkzeug.exceptions

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/findmespot"
# app.config["APPLICATION_ROOT"] = ""
# @app.route("/")
API_METHODS = {'test'}


@app.errorhandler(werkzeug.exceptions.BadRequest)
def internal_error_handler(e):
    message = {
        'status': 400,
        'message': 'API method not found: ' + request.url,
        'return': {'debug': str(e)}
    }
    response = jsonify(message)
    response.status_code = 400
    return response


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def internal_error_handler(e):
    message = {
        'status': 500,
        'message': 'Internal server error: ' + request.url,
        'return': {'debug': str(e)}
    }
    response = jsonify(message)
    response.status_code = 500
    return response


def test(args):
    message ={
        'status': 200,
        'message': 'OK',
        'return': dict(args)
    }
    response = jsonify(message)
    response.status_code = 200
    return response


@app.route(app.config['APPLICATION_ROOT'] + '/', defaults={'path': ''})  # Это — хук для того, чтобы обрабатывать пустой адрес и передавать в параметр пустой путь
@app.route(app.config['APPLICATION_ROOT'] + '/<path:path>')  # Это — хук для того, чтобы обрабатывать все адреса и передавать в параметр запрошенный путь
def hello(path):
    args = request.args
    if path == '':
        return 'It works!'
    else:
        if path in API_METHODS:
            return eval('{}({})'.format(path, dict(args)))
        else:
            return


app.wsgi_app = werkzeug.contrib.fixers.ProxyFix(app.wsgi_app)  # For Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0")
