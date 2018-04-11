from flask import Flask, jsonify, request, render_template
from prefix_and_wsgi_proxy_fix import ReverseProxied
import geojson
import werkzeug.exceptions
import sqlite3


app = Flask(__name__)
DB_DEFAULT_PATH = 'db/tracks.db'


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


@app.route('/get_waypoints')
def get_waypoints(*args, **kwargs):
    with sqlite3.connect(DB_DEFAULT_PATH) as con:
        cur = con.cursor()
        if 'trip_name' not in dict(request.args):
            return bad_request_error_handler(NameError(f'Key trip_name not found'))
        trip_name = dict(request.args)['trip_name'][0]
        table = cur.execute('''SELECT * FROM trips where name = ?''', (trip_name,))
        name, date_s, date_e, fms_id = table.fetchall()[0]
        waypoints = cur.execute('''SELECT * FROM waypoints where fms_key_id = ?''', (str(fms_id), )).fetchall()
        features = []
        for i in range(len(waypoints)):
            id, fms_key_id, id_fms, lat, long, alt, ts, bs, msg = waypoints[-(i + 1)]
            cur_point = geojson.Point((lat, long, alt))
            features.append(geojson.Feature(geometry=cur_point, properties={'BatteryState': bs,
                                                                          'Mesasage': msg,
                                                                          'TimeStamp': ts}))
        message = {
            'status': 200,
            'message': 'OK',
            'cnt': len(waypoints),
            'return': geojson.FeatureCollection(features)
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
