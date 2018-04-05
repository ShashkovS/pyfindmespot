from flask import Flask
from werkzeug.contrib.fixers import ProxyFix  # For Gunicorn

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = "/findmespot"
# @app.route("/")

@app.route('/', defaults={'path': ''})  # Это — хук для того, чтобы обрабатывать пустой адрес и передавать в параметр пустой путь
@app.route('/<path:path>')  # Это — хук для того, чтобы обрабатывать все адреса и передавать в параметр запрошенный путь
def hello(path):
    return """<h1>Flask app works here!</h1><p>Path is: """ + path + """."""


app.wsgi_app = ProxyFix(app.wsgi_app)  # For Gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0")
