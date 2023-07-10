import os
import pathlib
import requests
import json 
from flask import request, abort, redirect

from google.oauth2 import id_token

from pip._vendor import cachecontrol
import google.auth.transport.requests 
from googleapiclient.errors import HttpError



from datetime import datetime
from io import BytesIO

# Define the constants for Google API



class Loginer():
    def __init__(self, flow, kwargs):
        self.authorizer = Authorizer(flow)
        self.token = Token(flow, kwargs["GOOGLE_CLIENT_ID"])
        # self.credentials = flow.credentials
    

    def authorize(self, oauth):
        oauth.set_state(self.authorizer.get_state())
        return self.authorizer.get_url()# , self.authorizer.get_state()

    def verify_oauth_token_and_set_user_info(self, oauth):
        """Verify the OAuth token fetched from the request url and set the user info in the OAuth object.

        Args:
        oauth: A GoogleAPI object that handles OAuth operations.
        """
        # Fetch the token from the request url using the GoogleAPI object
        self.token.fetch(request.url)

        # Check if the state matches
        if not oauth.get_state() == request.args["state"]:
            abort(500)  #state does not match!

        # Verify the id token using the GoogleAPI object
        self.token.verify_id()

        # Set the google_id and name in the OAuth object
        oauth.set_google_id(self.token.get_id_info().get("sub"))
        oauth.set_name(self.token.get_id_info().get("name"))

class Authorizer():
    def __init__(self, flow):
        self.url, self.state = flow.authorization_url()
    
    def get_url(self):
        return self.url

    def get_state(self):
        return self.state

class Token():
    def __init__(self, flow, GOOGLE_CLIENT_ID, **kwargs):
        self.flow = flow
        self.google_client_id = GOOGLE_CLIENT_ID

    def fetch(self, request_url):
        # Fetch the token from the request url using the flow object
        self.flow.fetch_token(authorization_response=request_url)
    
    def verify_id(self):
        # Verify the id token using the credentials and the request object
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)
        self.id_info = id_token.verify_oauth2_token(
            id_token=self.flow.credentials._id_token,
            request=token_request,
            audience= self.google_client_id
        )
    
    def get_id_info(self):
        return self.id_info

    
    # Add any other methods for Google API as needed

