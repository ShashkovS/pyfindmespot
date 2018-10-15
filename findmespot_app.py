from flask import Flask, jsonify, request, render_template, Response
from prefix_and_wsgi_proxy_fix import ReverseProxied
import datetime
import gpxpy.gpx
import geojson
import werkzeug.exceptions
import sqlite3

app = Flask(__name__)
DB_DEFAULT_PATH = r'db\tracks.db'


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
    if 'trip_name' not in dict(request.args):
        return bad_request_error_handler(NameError(f'Key trip_name not found'))
    trip_name = dict(request.args)['trip_name'][0]
    with sqlite3.connect(DB_DEFAULT_PATH) as con:
        cur = con.cursor()
        table = cur.execute('''SELECT * FROM trips where name = ?''', (trip_name,))
        name, date_s, date_e, fms_id = table.fetchall()[0]
        waypoints = cur.execute('''SELECT * FROM waypoints where fms_key_id = ?''', (str(fms_id),)).fetchall()
        features = []
        for i in range(len(waypoints)):
            id, fms_key_id, id_fms, lat, long, alt, ts, bs, msg = waypoints[i]
            cur_point = geojson.Point((lat, long, alt))
            features.append(geojson.Feature(geometry=cur_point, properties={'BatteryState': bs,
                                                                            'Message': msg,
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


@app.route('/get_gpx_waypoints')
def generate_gpx(*args, **kwargs):
    if 'trip_name' not in dict(request.args):
        return bad_request_error_handler(NameError(f'Key trip_name not found'))
    trip_name = dict(request.args)['trip_name'][0]
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    with sqlite3.connect(DB_DEFAULT_PATH) as con:
        cur = con.cursor()
        table = cur.execute('''SELECT * FROM trips where name = ?''', (trip_name,))
        name, date_s, date_e, fms_id = table.fetchall()[0]
        waypoints = cur.execute('''SELECT * FROM waypoints where fms_key_id = ?''', (str(fms_id),)).fetchall()
        features = []
        for i in range(len(waypoints)):
            id, fms_key_id, id_fms, lat, long, alt, ts, bs, msg = waypoints[i]
            ts_time = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
            cur_pnt = gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=long, elevation=alt, comment=msg, time=ts_time)
            cur_pnt.description = f"Время: {ts}\n Заряд батареи {bs}\n"
            gpx_segment.points.append(cur_pnt)
    return Response(gpx.to_xml(), mimetype="text/xml")


@app.route('/')
def just_index():
    return render_template('index.html')


app.wsgi_app = ReverseProxied(app.wsgi_app)
if __name__ == "__main__":
    app.run(host="0.0.0.0")
