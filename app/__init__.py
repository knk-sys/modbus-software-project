from flask import Flask

def create_app():
    app = Flask(__name__)
    from . import routes  # Import routes to register the Blueprint
    app.register_blueprint(routes.bp)
    return app
