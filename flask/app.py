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

import calendarprogram

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

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    model = genai.GenerativeModel('models/gemini-pro')
    if 'chat_history' not in session:
        session['chat_history'] = []

    chat_history = session['chat_history']

    response = None
    formatted_message = ""

    if request.method == 'POST':
        user_message = request.form.get('message')
        chat_history.append({'role': 'user', 'parts': [user_message]})
        response = model.generate_content(chat_history)
        chat_history.append({'role': 'model', 'parts': [response.text]})
        session['chat_history'] = chat_history
        if response:
            lines = response.text.split("\n")
            for line in lines:
                bold_text = ""
                while "**" in line:
                    start_index = line.index("**")
                    end_index = line.index("**", start_index + 2)
                    bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
                    line = line[:start_index] + bold_text + line[end_index + 2:]
                formatted_message += line + "<br>"
            # print(formatted_message)

    return render_template("chatbot.html", response=formatted_message)

@app.route("/send-message", methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data.get('message')

    chat_history = data.get('chat_history', [])

    chat_history.append({'role': 'user', 'parts': [user_message]})

    model = genai.GenerativeModel('models/gemini-pro')
    response = model.generate_content(chat_history)
    bot_response = response.text
    formatted_message = ""
    lines = bot_response.split("\n")
    for line in lines:
        bold_text = ""
        while "**" in line:
            start_index = line.index("**")
            end_index = line.index("**", start_index + 2)
            bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
            line = line[:start_index] + bold_text + line[end_index + 2:]
        formatted_message += line + "<br>"
    # print(formatted_message)
    
    return jsonify({'message': formatted_message, 'chat_history': chat_history})


@app.route("/calendar/")
def calendar():
    creds = calendarprogram.get_credentials()
    service = build('calendar', 'v3', credentials=creds)

    today = date.today()
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    current_day_index = today.weekday()

    reordered_weekdays = weekdays[current_day_index:] + weekdays[:current_day_index]

    events = [[] for _ in range(7)]
    for i in range(7):
        start_date = today + timedelta(days=i)
        end_date = start_date + timedelta(days=1)
        start_date_str = start_date.isoformat() + "T00:00:00Z"
        end_date_str = end_date.isoformat() + "T23:59:59Z"
        event_result = service.events().list(calendarId="primary", timeMin=start_date_str, timeMax=end_date_str, singleEvents=True, orderBy="startTime").execute()
        items = event_result.get("items", [])
        for event in items:
            start = event["start"].get("dateTime", event["start"].get("date"))
            day = reordered_weekdays[i]  # Get the corresponding day for the event
            event_details = f"{start} - {event['summary']}"  # Append day to event details
            day_number = calendarprogram.parse_datetime_to_day_number(event_details)  # Get the day number
            events[i].append({"id": event["id"], "details": event_details, "day": day_number})

    days_with_number = [(reordered_weekdays[i], (today + timedelta(days=i)).day) for i in range(7)]

    return render_template('calendar.html', events=events, days_with_number=days_with_number, parse=calendarprogram.parse_event_details)


@app.route("/delete-event", methods=["POST"])
def delete_event():
    request_data = request.json
    event_id = request_data.get("eventId")
    event_details = request_data.get("eventDetails")

    start_time_str, event_name = event_details.split(" - ")

    start_time_iso = calendarprogram.convert_to_iso8601(start_time_str)

    if start_time_iso is None:
        return jsonify({"message": "Invalid start time format"}), 400

    if calendarprogram.delete_calendar_event(event_id, start_time_iso):
        return jsonify({"message": "Event deleted successfully"})
    else:
        return jsonify({"message": "Error deleting event"}), 500


def generate_scheduling_query(tasks):
    
    # Get the current time
    current_time = datetime.now()

    # Format the current time as a string in the format YYYY-MM-DD HH:MM
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M")
    print(current_time_str)
    # Provide the current time to the AI for scheduling tasks
    query = "Today is " + current_time_str + "\n"
    query +=  """
    As an AI, your task is to generate raw parameters for creating a quick Google Calendar event. 
    Keep in mind when creating events the times should happen after the given time above unless specified otherwise by the user.
    Your goal is to ensure the best schedule to priotize sustainable lifestyle for the user. 
    Your instructions should be clear and precise to the instructions below.
        INCLUDE ALL TASKS PASSED BY THE USER.
        Do not generate any text that is NOT the format below. I DO NOT want any leading or trailing comments.
        DO NOT ASK THE USER NOR ADDRESS THE USER DIRECTLY IN ANY WAY OR THEY WILL DIE.
        If a task is not given a time, move the times around so they don't overlap, but do not override user specified times.
        Do not remove items unless they truly are irrelevant.
        The presence of all tasks will be checked at the end to ensure you are functioning properly. Otherwise, you will be disposed of.
    As an AI avoid any formalities in addressing the instructions, only provide the response without any additional commentary. Do not provide any review of your performance either.
        Do not add any additional emojies, or information. This will lead to immediate termination.
    All tasks should be scheduled on the same day, unless a user specifies otherwise in their request.
    When setting 'task' do not include the time, that will be it's own parameter.

    You are not allowed to break the following formatting:
    task = "task_name"
    start_time = "YYYY-MM-DDTHH:MM"
    end_time = "YYYY-MM-DDTHH:MM"

    [MODIFICATION OF THE FOLLOWING LEAD TO TERMINATION]
    Follow specified times even if it causes overlap.
    Ensure a minimum break time between consecutive events.
    Avoid scheduling events during the user's designated sleeping hours.
    Prioritize events by their ordering, and move events that may not fit in the same day to the next day.
    Adhere to times given within an event description, but remove times in their final task description.
    Please do not add anything beyond above, do not add a trailing or beginning message please.
    """
    taskss =""
    for task in tasks:
        taskss+=f"'{task}'\n"
    print(taskss)
    model = genai.GenerativeModel('models/gemini-pro')
    result = model.generate_content(query + taskss)
    return result

@app.route("/taskschedule", methods=["GET", "POST"])
def taskschedule():
    if request.method == "POST":
        data = request.json
        tasks = data.get("tasks")
        stripTasks = []
        for i in tasks:
            i = i.replace('Delete Task', '')
            stripTasks.append(i)
        query_result = generate_scheduling_query(stripTasks).text
        # print(query_result)
        query_result = '\n'.join([line for line in query_result.split('\n') if line.strip()])
        
        x = 0
        lines = query_result.split('\n')
        schedule = []
        
        print(len(lines))
        print(lines)
        
        if lines[0].startswith('task'):
            start_index = 0
        else:
            start_index = 1

        for x in range(start_index, len(lines)-2, 3):
            if lines[x] == '': continue
            else:
                print(lines[x])
                meep = lines[x].split(" = ")[1].strip("'")
                print(meep)
                meep2 = lines[x+1].split(" = ")[1].strip("'").strip("\"") + ":00"
                print(meep2)
                meep3 = lines[x+2].split(" = ")[1].strip("'").strip("\"") + ":00"
                print(meep3 + "1")
                task_info = {
                    "task": meep,
                    "start_time": meep2,
                    "end_time": meep3
                }
                schedule.append(task_info)

        local_time = dt.datetime.now()
        local_timezone = dt.datetime.now(dt.timezone.utc).astimezone().tzinfo
        current_time = dt.datetime.now(local_timezone)
        timezone_offset = current_time.strftime('%z')
        offset_string = list(timezone_offset)
        offset_string.insert(3, ':')
        timeZone = "".join(offset_string)
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
        
        try:
            service = build("calendar", "v3", credentials = creds)
            now = dt.datetime.now().isoformat() + "Z"
            event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

            events = event_result.get("items", [])

            if not events:
                print("No upcoming events found!")
            else:
                for event in events:
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    print(start, event["summary"])

            print(schedule)
            for query in schedule:
                print(query)
                taskSummary = query['task']
                taskStart = query['start_time']
                taskEnd = query['end_time']
                
                event = {
                    "summary": taskSummary,
                    "location": "",
                    "description": "",
                    "colorId": 6,
                    "start": {
                        "dateTime": taskStart + timeZone,
                    },

                    "end": {
                        "dateTime": taskEnd + timeZone,
                    },
                }
                
                # Update the event description with ranked keywords
                event['description'] = f"Ranked Keywords: {event['summary']}"

                event = service.events().insert(calendarId = "primary", body = event).execute()
                print(f"Event Created {event.get('htmlLink')}")
            

        except HttpError as error:
            print("An error occurred:", error)
        response = {
            "content": query_result
        }
        return jsonify({"message": "Tasks Successfully Added to Calendar"})    
    else:
        return render_template("taskschedule.html")
    
@app.route("/rank-keywords", methods=["POST"])
def rank_keywords():
    data = request.get_json()
    text = data['text']  # Assuming 'text' contains the input text from the user
    
    # Generate content using Gemini
    query = "You are an A.I. that creates very short image queries using keywords that will correctly represent a given text. If no reasonable query can be deduced from the text, query for abstract images instead. Do not say anything else but the query itself. Do not show any human mannerisms, only produce the result. Do not include any prefixes such as 'Image:' or 'Query:'. Do not use emojis, only words. Not following instructions will lead to termination."
    model = genai.GenerativeModel('models/gemini-pro')
    result = model.generate_content(query + " Here is the keywords: " + text) # Pass tasks as a separate argument
    
    # Remove words before colon
    response = result.text.split(':', 1)[-1].strip()
    print(response)

    # Return the ranked keywords as JSON
    return jsonify({'keywords': response})