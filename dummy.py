from flask import Flask
from werkzeug.contrib.fixers import ProxyFix  # For Gunicorn
application = Flask(__name__)
@application.route("/")
def hello():
    return """<h1>Hello world!</h1>"""
application.wsgi_app = ProxyFix(application.wsgi_app)  # For Gunicorn
if __name__ == "__main__":
    application.run(host="0.0.0.0")

