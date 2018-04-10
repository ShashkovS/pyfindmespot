from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from random import randint
# import werkzeug.contrib.fixers
from prefix_proxy_fix import ReverseProxied
import werkzeug.exceptions

app = Flask(__name__)
# app.config["APPLICATION_ROOT"] = "/findmespot"
# app.config["APPLICATION_ROOT"] = ""
# @app.route("/")


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


@app.route('/')
def just_index():
    return render_template('index.html')

@app.route('/test')
def hello():
    return test()


# app.wsgi_app = werkzeug.contrib.fixers.ProxyFix(app.wsgi_app)  # For Gunicorn
app.wsgi_app = ReverseProxied(app.wsgi_app)  # For Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0")
