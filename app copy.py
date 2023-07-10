import os
import json 

from flask import (
    Flask, flash,
    redirect, request, 
    render_template, 
    session, url_for, 
    abort,
)
from oauth import OAuth
from authentication import API_Servicer
from werkzeug.utils import secure_filename

# Create a Flask app object
app = Flask("Slides Teaching System")
app.secret_key = "sts"  #it is necessary to set a password when dealing with OAuth 2.0
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

with open('config.json') as f:
    config = json.load(f)

# Create an OAuth object
oauth = OAuth()
# Create a GoogleAPI object
api_service = API_Servicer(config)# GoogleAPI()


@app.route("/login")  #the page where the user can login
def login():
    # Get the authorization url and state from the GoogleAPI object
    authorization_url= api_service.authorize(oauth) # state 
    # oauth.set_state(state)
    # Redirect to the authorization url
    return redirect(authorization_url)

@app.route("/callback")  #this is the page that will handle the callback process meaning process after the authorization
def callback():
    api_service.verify_oauth_token_and_set_user_info(oauth)
    # Redirect to the protected area
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

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file'] 
    if file and file.filename.endswith('.pptx'):   
        presentation_url =  api_service.upload_file(file).get('webViewLink') 
        
        return render_template(
            'play.html', 
            url=presentation_url
        )

@app.route('/record-audio')
def audio_rec():
    return render_template("rec_audio.html") # app.send_static_file('rec_audio.html') 


@app.route('/save-record', methods=['POST'])
def save_record():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']

    api_service.upload_file(file)
    

    return '<h1>Success</h1>'

@app.


if __name__ == "__main__":
    app.run(debug=True)