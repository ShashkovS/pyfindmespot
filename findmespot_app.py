from flask import Flask, jsonify, request, render_template
from prefix_and_wsgi_proxy_fix import ReverseProxied
import geojson
import werkzeug.exceptions
import random
import datetime

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


@app.route('/test')
def test(*args, **kwargs):
    am_dots = int(dict(request.args).get('amount', [10])[0])
    points = geojson.MultiPoint()
    for i in range(am_dots):
        points['coordinates'].append([random.uniform(-90.0, 90.0), random.uniform(0, 180.0), random.randint(0, 1000)]) # latitude, longitude, altitude
    message = {
        'status': 200,
        'message': 'OK',
        'return': geojson.Feature(geometry=points, properties={'track_name': 'Kerzhenec2018', 'amount': am_dots,
                                                               'time': datetime.datetime.now(),
                                                               'battery': 100})
    }
    response = jsonify(message)
    response.status_code = 200
    return response


@app.route('/')
def just_index():
    return render_template('index.html')


app.wsgi_app = ReverseProxied(app.wsgi_app)
if __name__ == "__main__":
    app.run(host="0.0.0.0")
