from flask import Flask, jsonify, request, render_template, Response, send_file
from prefix_and_wsgi_proxy_fix import ReverseProxied
from base64 import urlsafe_b64encode
import gpxpy.gpx
import geojson
import werkzeug.exceptions
import os
from werkzeug.datastructures import Headers
from db_functions import get_waypoints_by_trip, set_db_path, create_new_trip, str_ts_to_UTC_ts
from time_functions import str_ts_to_UTC_ts
from datetime import timedelta, timezone

app = Flask(__name__)
APP_PATH = os.path.dirname(os.path.realpath(__file__))
sqlite_db_path = os.path.join(APP_PATH, 'db', 'tracks_prod.db')
set_db_path(sqlite_db_path)


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
    args = dict(request.args)
    if 'trip_name' not in args:
        return bad_request_error_handler(NameError(f'Key trip_name not found'))
    trip_name = args['trip_name']
    waypoints = get_waypoints_by_trip(trip_name)
    features = []
    for i in range(len(waypoints)):
        id, fms_key_id, id_fms, lat, long, alt, ts, bs, msg = waypoints[i]
        ts = str_ts_to_UTC_ts(ts)
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

@app.route('/u')
def generate_iframe_html(*args, **kwargs):
    args = dict(request.args)
    if 'trip_name' not in args and 't' not in args:
        return bad_request_error_handler(NameError(f'Key trip_name not found'))
    trip_name = ''.join((args.get('trip_name', None) or args['t']))
    urlbase64 = f'[{{"n":"{trip_name}","c":3,"m":true,"u":"https://proj179.ru/pyfindmespot/gw?t={trip_name}"}}]'
    urlbase64 = urlsafe_b64encode(urlbase64.encode('utf-8')).decode('utf-8')
    return render_template('nakarte.html', urlbase64=urlbase64)


@app.route('/gw')
@app.route('/get_gpx_waypoints')
def generate_gpx(*args, **kwargs):
    args = dict(request.args)
    if 'trip_name' not in args and 't' not in args:
        return bad_request_error_handler(NameError(f'Key trip_name not found'))
    trip_name = ''.join((args.get('trip_name', None) or args['t']))
    waypoints = get_waypoints_by_trip(trip_name)
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    for i in range(len(waypoints)):
        id, fms_key_id, id_fms, lat, long, alt, ts, bs, msg = waypoints[i]
        ts = str_ts_to_UTC_ts(ts)
        if msg:
            gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(latitude=lat, longitude=long, elevation=alt, comment=msg, time=ts, name=msg))
        cur_pnt = gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=long, elevation=alt, comment=msg, time=ts)
        cur_pnt.description = f"Время: {ts} Заряд батареи {bs}"
        gpx_segment.points.append(cur_pnt)
    # Добавляем точку с временем последнего сообщения
    if waypoints:
        ts_msg = ts.astimezone(timezone(offset=timedelta(hours=+3))).strftime("%Y-%m-%d %H:%M:%S")
        gpx.waypoints.append(gpxpy.gpx.GPXWaypoint(latitude=lat, longitude=long, elevation=alt, comment=ts_msg, time=ts, name=ts_msg))
    hdrs = Headers()
    hdrs.add('Content-Type', 'application/gpx+xml')
    hdrs.add('Content-Disposition', 'attachment', filename='track.gpx')
    return Response(gpx.to_xml(), headers=hdrs)


@app.route('/create_track')
def create_track(*args, **kwargs):
    args = dict(request.args)
    for parm in ['trip_name', 'fms_key', 'date_s', 'date_e']:
        if parm not in args:
            return bad_request_error_handler(NameError(f'Key {parm} not found'))
    trip_name = args['trip_name']
    fms_key = args['fms_key']
    print(args)
    date_s = str_ts_to_UTC_ts(args['date_s'])
    date_e = str_ts_to_UTC_ts(args['date_e'])
    create_new_trip(trip_name, fms_key, date_s, date_e)
    message = {
        'status': 200,
        'message': 'OK'
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
