import io
import os
import json
from OpenSSL import SSL

from flask import (
    Flask, flash,
    redirect, request, Response,
    render_template,
    session, url_for,
    abort, send_from_directory
)
from flask_cors import CORS

from flask_cors import cross_origin

from google_auth_oauthlib.flow import Flow
from oauth import OAuth

from google_services.upload import GG_DriveFileUploader
from google_services import authentication, presentations

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from werkzeug.utils import secure_filename

import audio

# Text-to-speech
from gtts import gTTS
import tts

# Configure for objects:
with open('config.json') as f:
    config = json.load(f)


# Create a Flask app object
app = Flask("Slides Teaching System")
app.secret_key = "sts"  # it is necessary to set a password when dealing with OAuth 2.0
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
CORS(app, origins=["https://127.0.0.1:5000"])
# context = SSL.Context(SSL.TLSv1_2_METHOD)


# context.use_privatekey_file("server.key")
# context.use_certificate_file("server.crt")
# context.use_privatekey_file("server.key")
# context.use_certificate_file("server.crt")

# Initialize object
flow = Flow.from_client_secrets_file(
    client_secrets_file=config["client_secrets_file"],
    scopes=config['scopes'],
    redirect_uri=config["redirect_uri"]
)
oauth = OAuth()
loginer = authentication.Loginer(flow, config)  # GoogleAPI()
slide_ulity, file_uploader = [None]*2


def __init__():
    global file_uploader, slide_ulity
    slide_ulity = presentations.SlidesUtils(flow)
    file_uploader = GG_DriveFileUploader(flow)


@app.route("/login")  # the page where the user can login
def login():
    # Get the authorization url and state from the GoogleAPI object
    authorization_url = loginer.authorize(oauth)  # state

    # Redirect to the authorization url
    return redirect(authorization_url)


# this is the page that will handle the callback process meaning process after the authorization
@app.route("/callback")
def callback():
    loginer.verify_oauth_token_and_set_user_info(oauth)
    # Redirect to the protected area
    __init__()
    # print_cmt(flow.credentials)

    # print(get_speaker_notes("1spmrPZeOJbSwttjYyo2-MTa2R9Vkx9IV67iXvRiYjFI", "g22f0867fb07_7_49"))
    return redirect(url_for("welcome"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"


@app.route("/welcome")
@oauth.login_is_required
def welcome():
    return f"Welcome, {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"


@app.route('/upload_slide')
def upload_slides():
    return render_template('upload_slide.html')

# Python


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and (file.filename.endswith('.pptx') or file.filename.endswith('.ppt')):
        upload_state = file_uploader.upload(file)
        presentation_url = upload_state.get('webViewLink')

        print(upload_state)

        return render_template(
            'play.html',
            url=presentation_url,
            slide_url=presentation_url + "#slide=id.p1"  # Thêm dòng này
        )


@app.route('/record-audio')
def audio_rec():
    # app.send_static_file('rec_audio.html')
    return render_template("rec_audio.html")


@app.route('/save-record', methods=['POST'])
def save_record():
    # check if the post request has the file part
    if not file_uploader:
        flash('No file part')
        return abort(401)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    audio_file = audio.converts_to_mp4(file)
    file_uploader.upload_audio(audio_file)
    return '<h1>Success</h1>'


@app.route('/read_content')
def read_content():
    return render_template('tts.html')






"""@app.route('/read', methods=['POST'])
def read():
    data = tts.read_content()
    return Response(data, mimetype='audio/mpeg')"""


@app.route("/speak/<presentation_id>/<slide_number>")
def speak(presentation_id, slide_number):
    print(slide_number)
    # Get the slide id by concatenating "p" and slide_number
    slide_id = "p" + slide_number
    # Get tahe speaker notes text from the get_speaker_notes function
    note = slide_ulity.get_speaker_note(presentation_id, slide_id)
    print(note)
    data = tts.read_content(note)

    return Response(data, mimetype="audio/mpeg")


@app.route("/play_slides/<presentation_id>")
def play_slides_route(presentation_id):
    presentation_url, slide_url = slide_ulity.get_slides_url(presentation_id)
    return render_template("play_slides.html", url=presentation_url, slide_url=slide_url)


@app.route("/import_audio/<audio_id>/<presentation_id>/<slide_number>")
def import_audio(audio_id, presentation_id, slide_number):
    slide_id = "p{}".format(slide_number)
    slide_ulity.import_audio(audio_id, presentation_id, slide_id)
    return Response("Audio inserted successfully", status=200)




from googleapiclient.discovery import build
from flask import Flask, request, Response, render_template
from io import BytesIO # Import BytesIO module

# Create a service object for Google Drive API v3
drive_service = build('drive', 'v3', credentials=credentials)

# Create a service object for Google Slides API v1
slides_service = build('slides', 'v1', credentials=credentials)

# Create a Flask app object
app = Flask(__name__)

@app.route("/record_audio/<presentation_id>/<slide_number>", methods=["GET"])
def record_audio(presentation_id, slide_number):
    # Render a template HTML from rec_audio.html
    return render_template("rec_audio.html", presentation_id=presentation_id, slide_number=slide_number)

@app.route("/save_record/<presentation_id>/<slide_number>", methods=["POST"])
def save_record(presentation_id, slide_number):
    # Get the audio file from the form data of the request
    audio_file = request.files.get("audio")
    if not audio_file:
        return Response("No audio file found", status=400)

    # Upload the audio file to Google Drive using Google Drive API
    file_metadata = {
        "name": audio_file.filename,
        "mimeType": "video/mp4" # Change the MIME type to video/mp4
    }
    media = MediaFileUpload(BytesIO(audio_file.stream.read())) # Convert audio_file.stream to a BytesIO object
    drive_file = drive_service.files().create(body=file_metadata, media_body=media).execute()
    # Get the id of the audio file on Google Drive
    audio_id = drive_file.get("id")

    # Create the slide id by concatenating "p" and slide_number
    slide_id = "p" + slide_number

    # The size of the audio in EMU (1 cm = 360000 EMU).
    audio_size = {
        "width": {
            "magnitude": 3000000,
            "unit": "EMU"
        },
        "height": {
            "magnitude": 3000000,
            "unit": "EMU"
        }
    }

    # The transform of the audio in EMU (1 cm = 360000 EMU).
    audio_transform = {
        "scaleX": 1,
        "scaleY": 1,
        "translateX": 311708,
        "translateY": 744575,
        "unit": "EMU"
    }

    # Create a batchUpdate request with a createVideo request using Google Slides API
    requests = [
        {
            "createVideo": {
                "source": "DRIVE",
                "id": audio_id,
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": audio_size,
                    "transform": audio_transform
                }
            }
        }
    ]

    # Execute the request and handle the response
    try:
        response = slides_service.presentations().batchUpdate(presentationId=presentation_id, body={"requests": requests}).execute()
        print(response)
        return Response("Audio inserted successfully", status=200)
    except Exception as e:
        print(e)
        return Response("An error occurred", status=400)



# 1BJtDZ7XGHc0IKvDGC3nFPhmFh_x9Hcc6Dsw9ubx_e5s
# 1spmrPZeOJbSwttjYyo2-MTa2R9Vkx9IV67iXvRiYjFI,  g22f0867fb07_7_49
# 1fUcWO-DTGb9Xlb5W6nICbK_pwHXMhmqUIipJrvToyKQ
if __name__ == "__main__":
    # app.run(ssl_context=('cert.pem', 'key.pem'))
    app.run(debug=True, port=5000, ssl_context=(
        './server.crt', './server.key'))

# Test the function with a sample presentation id
# print(get_speaker_notes("12SQU9Ik-ShXecJoMtT-LlNwEPiFR7AadnxV2KiBXCnE"))
