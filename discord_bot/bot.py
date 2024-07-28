import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import random
import schedule
import datetime

import regular_response
import user_response
import task_response
from user import User, UserDatabase

from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

load_dotenv()

def run_discord_bot():
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.all()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    userDatabase = UserDatabase('user_database.db')
    time_dictionary = {}
    user_list = userDatabase.get_all_users()
    
    time_example = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    for user_index in user_list:
        if user_index[1] not in time_dictionary:
            time_dictionary[user_index[1]] = [user_index[2], False]

    @bot.event
    async def on_ready():
        print(f'{bot.user} is now running!')
        try:
            synced = await bot.tree.sync()
            print(f'Synced {synced} command(s)')
            print(f'Synced {len(synced)} command(s)')
            bot.loop.create_task(ping_at_specific_time(bot, time_dictionary))
        except Exception as e:
            print(e)     
    
    async def ping_at_specific_time(bot : commands.Bot, time_dictionary : dict):
        while True:            
            userDatabase = UserDatabase('user_database.db')            
            user_list = userDatabase.get_all_users()
            for user_index in user_list:
                if user_index[1] not in time_dictionary:
                    time_dictionary[user_index[1]] = [user_index[2], False]
                if (user_index[1] in time_dictionary and time_dictionary[user_index[1]][0] != user_index[2]):
                    time_dictionary[user_index[1]] = [user_index[2], False]
            current_time = datetime.datetime.now().strftime("%H:%M")
            if current_time == "00:00":
                for users in time_dictionary:
                    time_dictionary[users][1] = False
            print(time_dictionary)
            for users in time_dictionary:
                if current_time == time_dictionary[users][0] and time_dictionary[users][1] == False:
                    creds = None
                    username_string = f'token/token_{users}.json'
                    if os.path.exists(username_string):
                        creds = Credentials.from_authorized_user_file(username_string, SCOPES)        

                    if not creds or not creds.valid:
                        if creds and creds.expired and creds.refresh_token:
                            try:
                                creds.refresh(Request())
                            except Exception as e:
                                if os.path.exists(username_string):
                                    os.remove(username_string)
                        else:
                            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                            creds = flow.run_local_server(port = 0)

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
                    print(f'{current_time} BOT PINGED FOR {users}')
                    user = await bot.fetch_user(user_index[1])
                    result_title = f'**Today Tasks:**'
                    result_description = f'**{user_index[0]}\'s tasks**'
                    embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                    file = discord.File('images/icon.png', filename='icon.png')
                    embed.set_thumbnail(url='attachment://icon.png')
                    embed.set_author(name="Reminder-Bot says:")
                    if len(sorted_data) > 0:
                        for item in sorted_data:
                            string = f'**Start Time: ** {datetime.datetime.strptime(item['start']['dateTime'][:19], "%Y-%m-%dT%H:%M:%S").strftime("%B %d, %Y %I:%M:%S %p")}\n**End Time: **{datetime.datetime.strptime(item['end']['dateTime'][:19], "%Y-%m-%dT%H:%M:%S").strftime("%B %d, %Y %I:%M:%S %p")}\n**Link: **{item['htmlLink']}'
                            embed.add_field(name=item['summary'].replace('"', ''), value=string, inline=False)
                    else:
                        embed.add_field(name="No Tasks Schedule For Today", value="Have A Great Day!", inline=False)
                    embed.set_footer(text=bot.user.mention)
                    await user.send(file=file, embed=embed)
                    time_dictionary[users][1] = True
            userDatabase.close()
            await asyncio.sleep(60)
    
    @bot.tree.command(name = "hello", description = "Bot Returns a Greeting!")
    async def hello(interaction : discord.Interaction):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')
        await regular_response.hello(interaction)

    @bot.tree.command(name = "time", description = "Bot Returns the Current Time!")
    async def time(interaction : discord.Interaction):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')
        await regular_response.time(interaction)
        
    @bot.tree.command(name = "adduser", description = "Adds user to Bot Database and Connects Google Calendar!")
    @app_commands.describe(time_reminder = "What time do you want to be reminded?")
    async def adduser(interaction : discord.Interaction, time_reminder : str):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message} with parameters: {time_reminder}" ({channel})')
        await user_response.adduser(interaction, time_reminder, userDatabase)

    @bot.tree.command(name = "userinfo", description = "Bot Returns the User Information!")
    async def userinfo(interaction : discord.Interaction):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')
        await user_response.userinfo(interaction, userDatabase)

    @bot.tree.command(name = "changereminder", description = "Bot Changes Reminder Time!")
    @app_commands.describe(time_reminder = "What time do you want to change it to?")
    async def changereminder(interaction : discord.Interaction, time_reminder : str):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')
        await user_response.changereminder(interaction, time_reminder,userDatabase)

    @bot.tree.command(name = "deleteuser", description = "Bot Deletes User from the Database!")
    async def changereminder(interaction : discord.Interaction):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')
        await user_response.deleteuser(interaction, userDatabase)

    @bot.tree.command(name = "addtask", description = "Bot Adds a Task to the User's Google Calendar!")
    @app_commands.describe(task_name = "Enter Task Name", task_start = f"Enter Task Start Time in **YEAR-MONTH-DATETHOUR:MINUTE:SECONDS**", task_end = f"Enter Task End Time in **YEAR-MONTH-DATETHOUR:MINUTE:SECONDS**")
    async def addtask(interaction : discord.Interaction, task_name : str, task_start : str, task_end : str):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message} with parameters: {task_name}, {task_start}, {task_end}" ({channel})')
        await task_response.addtask(interaction, task_name, task_start, task_end, userDatabase)

    @bot.tree.command(name = "todaytask", description = "Bot Shows Tasks for Today!")
    async def todaytask(interaction : discord.Interaction):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')
        await task_response.todaytask(interaction, userDatabase)

    @bot.tree.command(name = "alltasks", description = "Bot Shows All of the Tasks on the Calendar!")
    async def alltask(interaction : discord.Interaction):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')
        await task_response.alltask(interaction, userDatabase)

    @bot.tree.command(name = "removetask", description = "Bot Removes a Tasks From the Calendar!")    
    @app_commands.describe(task_name = "What task do you want to delete?")
    async def removetask(interaction : discord.Interaction, task_name : str):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')
        await task_response.removetask(interaction, task_name, userDatabase)

    @bot.tree.command(name = "pomodoro", description = "Starts a Pomodoro Clock!")
    @app_commands.describe(pomodoro_start = "Enter Work Minutes", pomodoro_break = "Enter Break Minutes", intervals = "Enter How Many Times You Want to Run")
    async def pomodoro(interaction : discord.Interaction, pomodoro_start : str, pomodoro_break : str, intervals : str):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message} with parameters: {pomodoro_start}, {pomodoro_break}, {intervals}" ({channel})')
        await regular_response.pomodoro(interaction, pomodoro_start, pomodoro_break, intervals, userDatabase)

    @bot.tree.command(name = "help", description = "Bot Shows All Commands for Reminder-Bot!")
    async def help(interaction : discord.Interaction):
        username = str(interaction.user)
        mention = str(interaction.user.mention)
        user_message = str(interaction.command.name)
        channel = str(interaction.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')
        await task_response.help(interaction)

    bot.run(TOKEN)
    