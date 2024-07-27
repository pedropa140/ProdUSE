from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g, session, send_file, secure, send_from_directory
import json
import os
from os import path, urandom
from dotenv import load_dotenv
import requests
import PyPDF2
import pymongo
import random
import regex
from werkzeug.utils import secure_filename
import subprocess
from datetime import date, datetime, timedelta, timezone
import datetime as dt
import uuid
import subprocess

import google.generativeai as genai
from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.generativeai import generative_models
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from authlib.integrations.flask_client import OAuth
SCOPES = ['https://www.googleapis.com/auth/calendar',  'https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/documents'] # USE SCOPES FOR CREDENTIALS
# GET CREDENTIALS LATER

app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URL")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.context_processor
def inject_exists_credentials():
    return {'exists_credentials': os.path.exists('credentials.json')}

@app.route("/")
def mainpage():
    return render_template("main.html")

oauth = OAuth(app)
oauth.register(
    "oauthApp",
    client_id='GSlRU8ssqQmC7BteFwhCLqxonlmtvSBP',
    client_secret='4YFxFjzvuXtXyYMoJ9coyCHDphXdUYMAGNF3gcwpZh16Hv-Hz_s83TqawI0RmR2b',
    api_base_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com',
    access_token_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com/oauth/token',
    authorize_url='https://dev-jkuyeavh0j4elcuc.us.auth0.com/oauth/authorize',
    client_kwargs={'scope': 'scope_required_by_provider'}
)

def get_db():
    client = pymongo.MongoClient(MONGODB_URI)
    db = client.get_default_database()
    return db

@app.route("/signup", methods=["GET", "POST"])
def signup():
    auth_params = {"screen_hint": "signup"}
    return oauth.create_client("oauthApp").authorize_redirect(redirect_uri=url_for('authorized', _external=True), **auth_params)

@app.route("/login", methods=["GET", "POST"])
def login():
    return oauth.create_client("oauthApp").authorize_redirect(redirect_uri=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    if os.path.exists('token.json'):
        os.remove('token.json')
    
    return redirect(url_for('mainpage'))

def get_auth0_client_info():
    response = requests.get(AUTH0_API_ENDPOINT)

    if response.status_code == 200:
        auth0_info = response.json()
        return auth0_info
    else:
        raise Exception(f"Failed to retrieve Auth0 client info: {response.status_code} - {response.text}")

@app.route('/authorized')
def authorized():
    token = oauth.oauthApp.authorize_access_token()
    oauth_token = token['access_token']
    session['oauth_token'] = oauth_token

    if not path.exists("credentials.json"):
        credentials = {
            "client_id": re,
            "client_secret": 'YOUR_CLIENT_SECRET',
            "auth_uri": 'YOUR_AUTH_URI',
            "token_uri": 'YOUR_TOKEN_URI',
            "auth_provider_x509_cert_url": 'YOUR_AUTH_PROVIDER_CERT_URL'
        }

        with open('credentials.json', 'w') as file:
            json.dump(credentials, file)
            
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                if os.path.exists("token.json"):
                    os.remove("token.json")
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port = 0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())
    
    global user_logged_in
    user_logged_in = True
    return redirect(url_for('education'))