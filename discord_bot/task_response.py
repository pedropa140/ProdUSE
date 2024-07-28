import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import random
import datetime
import regex as re

from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

from user import User, UserDatabase

async def addtask(interaction: discord.Interaction, task_name : str, task_start : str, task_end : str, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(interaction.user.id)):       
        def validate_time(time_str):
            pattern = r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$'
            match = re.match(pattern, time_str)                
            if not match:
                return False
            year, month, day, hour, minute, second = map(int, match.groups())
            if not (1 <= month <= 12 and 1 <= day <= 31 and 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                return False
            if month == 2 and day > 28:
                return False                
            return True
        start_check = validate_time(task_start)
        end_check = validate_time(task_end)
        if not start_check:
            result_title = f'Invalid Output'
            result_description = f'Time should be in **YEAR-MONTH-DATETHOUR:MINUTE:SECONDS** format for **{interaction.user.mention}**'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="Reminder-Bot says:")
            example = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            embed.add_field(name="Please enter in {YEAR}-{MONTH}-{DAY}T{HOUR}:{MINUTE}:{SECOND}", value=example)
            embed.set_footer(text="/changereminder")
            await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
            return
        
        username_string = f'token/token_{str(interaction.user.id)}.json'
        if os.path.exists(username_string):
            creds = Credentials.from_authorized_user_file(username_string, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists(username_string):
                        os.remove(username_string)

                with open(username_string, "w") as token:
                    token.write(creds.to_json())
        local_time = datetime.datetime.now()
        local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        current_time = datetime.datetime.now(local_timezone)
        timezone_offset = current_time.strftime('%z')
        offset_string = list(timezone_offset)
        offset_string.insert(3, ':')
        timeZone = "".join(offset_string)
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        datetime_stuff = datetime.datetime.now()
        today_date = f'{datetime_stuff.year}-{datetime_stuff.month}-{datetime_stuff.day}T'
        taskSummary = task_name
        taskStart = task_start
        taskEnd = task_end
        event = {
            'summary': taskSummary,
            'start': {
                'dateTime': taskStart,
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': taskEnd,
                'timeZone': 'America/New_York',
            },
        }
        event = service.events().insert(calendarId = "primary", body = event).execute()

        result_title = f'**Task Created**'
        result_description = 'Task Description:'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.add_field(name="Task Name", value=taskSummary, inline=False)
        start = datetime.datetime.strptime(taskStart, "%Y-%m-%dT%H:%M:%S")
        end = datetime.datetime.strptime(taskEnd, "%Y-%m-%dT%H:%M:%S")
        embed.add_field(name="Task Start Date", value=start.strftime("%B %d, %Y %I:%M:%S %p"), inline=False)
        embed.add_field(name="Task End Date", value=end.strftime("%B %d, %Y %I:%M:%S %p"), inline=False)
        embed.add_field(name="Link", value=event.get('htmlLink'), inline=False)
        embed.set_footer(text="/addtask")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
    else:
        result_title = f'Account Not Found'
        result_description = f'User not found for for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/addtask")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)

async def todaytask(interaction : discord.Interaction, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(interaction.user.id)):
        creds = None
        username_string = f'token/token_{str(interaction.user.id)}.json'
        if os.path.exists(username_string):
            creds = Credentials.from_authorized_user_file(username_string, SCOPES)        

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists(username_string):
                        os.remove(username_string)

                with open(username_string, "w") as token:
                    token.write(creds.to_json())
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

        events = event_result.get("items", [])
        def convert_to_datetime(date_str):
            try:
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                print(f"Error: Invalid date string encountered: {date_str}")
                return None
        today_date = datetime.datetime.today().date()
        today_tasks = [task for task in events if convert_to_datetime(task['end']['dateTime'][:19]).date() == today_date]
        sorted_data = sorted(today_tasks, key=lambda x: x['end']['dateTime'])
        result_title = f'**Today Tasks:**'
        result_description = f'**{interaction.user.mention}\'s tasks**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        if len(sorted_data) > 0:
            for item in sorted_data:
                string = f'**Start Time: ** {datetime.datetime.strptime(item['start']['dateTime'][:19], "%Y-%m-%dT%H:%M:%S").strftime("%B %d, %Y %I:%M:%S %p")}\n**End Time: **{datetime.datetime.strptime(item['end']['dateTime'][:19], "%Y-%m-%dT%H:%M:%S").strftime("%B %d, %Y %I:%M:%S %p")}\n**Link: **{item['htmlLink']}'
                embed.add_field(name=item['summary'].replace('"', ''), value=string, inline=False)
        else:
            embed.add_field(name="No Tasks Schedule For Today", value="Have A Great Day/", inline=False)
        embed.set_footer(text="/todaytask")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
    else:
        result_title = f'Account Not Found'
        result_description = f'User not found for for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/todaytask")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)

async def alltask(interaction : discord.Interaction, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(interaction.user.id)):
        creds = None
        username_string = f'token/token_{str(interaction.user.id)}.json'
        if os.path.exists(username_string):
            creds = Credentials.from_authorized_user_file(username_string, SCOPES)        

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists(username_string):
                        os.remove(username_string)

                with open(username_string, "w") as token:
                    token.write(creds.to_json())
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

        events = event_result.get("items", [])
        def convert_to_datetime(date_str):
            try:
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                print(f"Error: Invalid date string encountered: {date_str}")
                return None
        today_tasks = [task for task in events]
        sorted_data = sorted(today_tasks, key=lambda x: x['end']['dateTime'])
        result_title = f'**Today Tasks:**'
        result_description = f'**{interaction.user.mention}\'s tasks**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        if len(sorted_data) > 0:
            for item in sorted_data:
                string = f'**Start Time: ** {datetime.datetime.strptime(item['start']['dateTime'][:19], "%Y-%m-%dT%H:%M:%S").strftime("%B %d, %Y %I:%M:%S %p")}\n**End Time: **{datetime.datetime.strptime(item['end']['dateTime'][:19], "%Y-%m-%dT%H:%M:%S").strftime("%B %d, %Y %I:%M:%S %p")}\n**Link: **{item['htmlLink']}'
                embed.add_field(name=item['summary'].replace('"', ''), value=string, inline=False)
        else:
            embed.add_field(name="No Tasks Schedule For Today", value="Have A Great Day/", inline=False)
        embed.set_footer(text="/todaytask")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
    else:
        result_title = f'Account Not Found'
        result_description = f'User not found for for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/todaytask")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)

async def removetask(interaction : discord.Interaction, task_name : str, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(interaction.user.id)):
        username_string = f'token/token_{str(interaction.user.id)}.json'
        if os.path.exists(username_string):
            creds = Credentials.from_authorized_user_file(username_string, SCOPES)        

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists(username_string):
                        os.remove(username_string)

                with open(username_string, "w") as token:
                    token.write(creds.to_json())
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()
        events = event_result.get("items", [])
        if len(events) == 0:
            result_title = f'**Error**'
            result_description = f'No Tasks On Your Schedule/'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="Reminder-Bot says:")
            embed.set_footer(text="/removetask")
            await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
        else:
            sorted_data = sorted(events, key=lambda x: x['end']['dateTime'])
            # if 0 < int(removetask_action_content) < len(sorted_data) + 1 and removetask_action_content.isdigit():
            #     service.events().delete(calendarId='primary', eventId=sorted_data[int(removetask_action_content) - 1]['id']).execute()
            #     result_title = f'**Task Deleted**'
            #     result_description = f'**{sorted_data[int(removetask_action_content) - 1]['summary']}** has been deleted/'
            #     embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            #     file = discord.File('images/icon.png', filename='icon.png')
            #     embed.set_thumbnail(url='attachment://icon.png')
            #     embed.set_author(name="Reminder-Bot says:")
            #     embed.set_footer(text="/removetask")
            #     await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
            check = False
            counter = 0
            for event in sorted_data:
                if task_name == event['summary']:
                    check = True
                    break
                counter += 1
            if check:
                service.events().delete(calendarId='primary', eventId=sorted_data[counter]['id']).execute()
                result_title = f'**Task Deleted**'
                result_description = f'**{sorted_data[counter]['id']}** has been deleted/'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="Reminder-Bot says:")
                embed.set_footer(text="/removetask")
                await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
            else:
                result_title = f'**Error**'
                result_description = f'Invalid Input. Please try again.'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="Reminder-Bot says:")
                embed.set_footer(text="/removetask")
                await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
    else:
        result_title = f'Account Not Found'
        result_description = f'User not found for for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/removetask")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)

