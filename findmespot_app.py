from flask import Flask, jsonify, request, render_template
from prefix_and_wsgi_proxy_fix import ReverseProxied
import geojson
import werkzeug.exceptions

app = Flask(__name__)


# This is just a test route. It is autotested after deploy
@app.route('/test_app_is_working_kQK74RxmgPPm69')
def test_app_is_working():
    return "Yup! The app is working!\n"


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


def test(*args, **kwargs):
    message = {
        'status': 200,
        'message': 'OK',
        'return': geojson.MultiPoint(((39.9669917, 44.2069527), (40.0135327, 44.2121987), (40.0317781, 44.2076412),
                                      (40.0376057, 44.1994963), (40.0293180, 44.2000179), (39.9953541, 44.2003035), ))
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


app.wsgi_app = ReverseProxied(app.wsgi_app)
if __name__ == "__main__":
    app.run(host="0.0.0.0")
