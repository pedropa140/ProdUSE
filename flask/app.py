from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g, session, send_file, secure, send_from_directory
import json
from os import path, urandom
from dotenv import load_dotenv
import requests
import PyPDF2
import random

from werkzeug.utils import secure_filename
import subprocess
from datetime import date, datetime, timedelta, timezone
import datetime as dt
import uuid
import subprocess

app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def mainpage():
    return render_template("main.html")