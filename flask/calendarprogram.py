import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

SCOPES = 'https://www.googleapis.com/auth/calendar'

def addSchedule(name, description, location, date, startTime, endTime):
    local_time = datetime.datetime.now()
    local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    current_time = datetime.datetime.now(local_timezone)
    timezone_offset = current_time.strftime('%z')
    offset_string = list(timezone_offset)
    offset_string.insert(3, ':')
    timeZone = "".join(offset_string)
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port = 0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

        events = event_result.get("items", [])

        if not events:
            print("No upcoming events found!")
        else:
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])

        event = {
            "summary": name,
            "location": location,
            "description": description,
            "colorId": 6,
            "start": {
                "dateTime": f"{date}T{startTime}:00" + timeZone,
            },

            "end": {
                "dateTime": f"{date}T{endTime}:00" + timeZone,
            },
        }


        event = service.events().insert(calendarId = "primary", body = event).execute()
        print(f"Event Created {event.get('htmlLink')}")

    except HttpError as error:
        print("An error occurred:", error)

    def get_credentials():
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds


    import datetime

    def delete_calendar_event(event_id, start_time_str):
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)
        
        try:
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
        except HttpError as e:
            if e.resp.status == 404:
                print("Event ID not found. Trying to find event by start time...")
                try:
                    start_time = datetime.datetime.fromisoformat(start_time_str)
                    end_time = start_time + datetime.timedelta(minutes=1)
                    start_time_iso = start_time.isoformat()
                    end_time_iso = end_time.isoformat()

                    events_result = service.events().list(calendarId='primary', timeMin=start_time_iso, timeMax=end_time_iso).execute()
                    events = events_result.get('items', [])
                    if events:
                        event_id_to_delete = events[0]['id']
                        service.events().delete(calendarId='primary', eventId=event_id_to_delete).execute()
                        return True
                    else:
                        print("Event not found by start time.")
                        return False
                except Exception as e:
                    print(f"Error deleting event by start time: {e}")
                    return False
            else:
                print(f"Error deleting event by ID: {e}")
                return False
            
    def parse_event_details(event_details):
        datetime_str, description = event_details.split(' - ')
        datetime_obj = datetime.fromisoformat(datetime_str)
        formatted_date = datetime_obj.strftime('%B %d')
        formatted_time = datetime_obj.strftime('%I:%M %p')
        end_time = (datetime_obj + timedelta(hours=1)).strftime('%I:%M %p')
        user_friendly_details = f"{description}<br><br>{formatted_time} - {end_time}"

        return user_friendly_details

    def convert_to_iso8601(start_time_str):
        try:
            start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S%z")
            return start_time.isoformat()
        except ValueError:
            return None

    from datetime import datetime

    def parse_datetime_to_day_number(datetime_str):
        datetime_obj = datetime.strptime(datetime_str.split(' - ')[0], '%Y-%m-%dT%H:%M:%S%z')
        day_number = datetime_obj.day

        return day_number

if __name__ == "__main__":
    addSchedule("meep", "can i get a meep yall", "ur mom house", "2024-03-30", "16:00", "18:00")
