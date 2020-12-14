from config import Config
from flask_login.utils import login_required
from app import app
from flask import Flask, render_template, Response, redirect, request
import os
from importlib import import_module
from flask_login import login_required, LoginManager, current_user, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera


appConfig = Config()

client = WebApplicationClient(appConfig.GOOGLE_CLIENT_ID)

@app.route('/')
@login_required
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login')
def login():
    google_provider_cfg = appConfig .get_google_provider_cfg()
    authorization_endpoint  = google_provider_cfg['authorization_endpoint']
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
            scope=["openid", "email", "profile"],
        )
    return redirect(request_uri)

@app.route('/login/callback')
def callback():
    code = request.args.get("code")