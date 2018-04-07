from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from random import randint
import werkzeug.contrib.fixers
import werkzeug.exceptions

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/findmespot"
# app.config["APPLICATION_ROOT"] = ""
# @app.route("/")
API_METHODS = {'test', 'test2'}


@app.errorhandler(werkzeug.exceptions.BadRequest)
def bad_request_error_handler(e=None):
    message = {
        'status': 400,
        'message': 'Bad request or API method not found: ' + request.url,
        'return': {'debug': str(e)}
    }
    response = jsonify(message)
    response.status_code = 400
    return response


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def internal_error_handler(e=None):
    message = {
        'status': 500,
        'message': 'Internal server error: ' + request.url,
        'return': {'debug': str(e)}
    }
    response = jsonify(message)
    response.status_code = 500
    return response


def test2(args):
    am = int(args.get('am', [10])[0])
    message = {
        'status': 200,
        'message': 'OK',
        'return': {'num_points': am,
                   'result': {}}
    }
    for i in range(am):
        message['return']['result'][i] = {'latitude': randint(0, 90),
                                'longitude': randint(0, 180)}
    response = jsonify(message)
    response.status_code = 200
    return response


def test(args):
    message = {
        'status': 200,
        'message': 'OK',
        'return': {'num_points': 1,
                   'result': {'latitude': randint(0, 90),
                   'longitude': randint(0, 180)}}
    }
    response = jsonify(message)
    response.status_code = 200
    return response


@app.route(app.config["APPLICATION_ROOT"] + '/', defaults={'path': ''})  # Это — хук для того, чтобы обрабатывать пустой адрес и передавать в параметр пустой путь
@app.route(app.config["APPLICATION_ROOT"] + '/<path:path>')  # Это — хук для того, чтобы обрабатывать все адреса и передавать в параметр запрошенный путь
def hello(path):
    args = request.args
    print(path)
    if path == '':
        return render_template('index.html')
    else:
        if path in API_METHODS:
            return eval('{}({})'.format(path, dict(args)))
        else:
            return bad_request_error_handler(NameError(f'Method {path} not found'))


app.wsgi_app = werkzeug.contrib.fixers.ProxyFix(app.wsgi_app)  # For Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0")
