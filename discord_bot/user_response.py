import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import random
import datetime

from user import User, UserDatabase

from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from Google_Calendar_Flow import InstalledAppFlow2, _WSGIRequestHandler, _RedirectWSGIApp
from string import ascii_letters, digits
import webbrowser
import wsgiref.simple_server
import wsgiref.util

import google.auth.transport.requests
import google.oauth2.credentials

import google_auth_oauthlib.helpers

SCOPES = ['https://www.googleapis.com/auth/calendar']

async def adduser(interaction : discord.Interaction, time_reminder : str, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(interaction.user.id)):
        result_title = f'**User Already Created**'
        result_description = f'User already created for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/adduser")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
    else:
        
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
            else:
                _DEFAULT_AUTH_PROMPT_MESSAGE = (
                    "Please visit this URL to authorize this application: {url}"
                )
                """str: The message to display when prompting the user for
                authorization."""
                _DEFAULT_AUTH_CODE_MESSAGE = "Enter the authorization code: "
                """str: The message to display when prompting the user for the
                authorization code. Used only by the console strategy."""

                _DEFAULT_WEB_SUCCESS_MESSAGE = (
                    "The authentication flow has completed. You may close this window."
                )
                flow = InstalledAppFlow2.from_client_secrets_file("credentials.json", SCOPES)
                host="localhost"
                bind_addr=None
                port=8080
                authorization_prompt_message=_DEFAULT_AUTH_PROMPT_MESSAGE
                success_message=_DEFAULT_WEB_SUCCESS_MESSAGE
                open_browser=True
                redirect_uri_trailing_slash=True
                timeout_seconds=None
                token_audience=None
                browser=None
                
                await interaction.response.defer()

                wsgi_app = _RedirectWSGIApp(success_message)
                wsgiref.simple_server.WSGIServer.allow_reuse_address = False
                local_server = wsgiref.simple_server.make_server(
                    bind_addr or host, port, wsgi_app, handler_class=wsgiref.simple_server.WSGIRequestHandler
                )

                try:
                    redirect_uri_format = (
                        "http://{}:{}/" if redirect_uri_trailing_slash else "http://{}:{}"
                    )
                    flow.redirect_uri = redirect_uri_format.format(
                        host, local_server.server_port
                    )
                    auth_url, _ = flow.authorization_url()
                    # print(auth_url)
                    result_title = f'**ALLOW ACCESS**'
                    result_description = f'Please click on this link to allow access to Google Calendars**'
                    embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                    file = discord.File('images/icon.png', filename='icon.png')
                    embed.add_field(name="LINK", value=auth_url, inline=False)
                    embed.set_thumbnail(url='attachment://icon.png')
                    embed.set_author(name="Reminder-Bot says:")
                    embed.set_footer(text="/adduser")
                    await interaction.followup.send(file=file, embed=embed, ephemeral=False)

                    # if authorization_prompt_message:
                    #     print(authorization_prompt_message.format(url=auth_url))

                    local_server.timeout = timeout_seconds
                    local_server.handle_request()
                    authorization_response = wsgi_app.last_request_uri.replace("http", "https")
                    flow.fetch_token(
                        authorization_response=authorization_response, audience=token_audience
                    )
                finally:
                    local_server.server_close()

                # print(f'credentials: {flow.credentials}')
                creds = flow.credentials
                with open(username_string, "w") as token:
                    token.write(creds.to_json())
        
        def validate_time(time_str):
            hours, minutes = time_str.split(':')
            if not hours.isdigit() or not minutes.isdigit():
                return False
            hours = int(hours)
            minutes = int(minutes)
            if hours < 0 or hours > 24 or minutes < 0 or minutes > 60:
                return False
            return True
        check = validate_time(time_reminder)
        if check:
            userDatabase.add_user(User(str(interaction.user), str(interaction.user.id), time_reminder))
            result_title = f'**User Created**'
            result_description = f'User created for **{interaction.user.mention}**'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="Reminder-Bot says:")
            embed.set_footer(text="/adduser")
            await interaction.followup.send(file=file, embed=embed, ephemeral=False)
        else:
            result_title = f'Invalid Output'
            result_description = f'Did not create user for **{interaction.user.mention}**'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="Reminder-Bot says:")
            embed.set_footer(text="/adduser")
            await interaction.followup.send(file=file, embed=embed, ephemeral=False)

async def userinfo(interaction : discord.Interaction, userDatabase : UserDatabase):
    if not userDatabase.user_exists(str(interaction.user.id)):
        result_title = f'**User Not Found**'
        result_description = f'User not found for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/userinfo")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
    else:
        discord_id = str(interaction.user.id)
        info = userDatabase.get_user_by_id(discord_id)
        result_title = f'Information about {info[0]}'
        description_string = f'**Name:**\t\t{info[0]}\n**Discord ID:**\t{info[1]}\n**Preferred Time:**\t{info[2]}'
        embed = discord.Embed(title=result_title, description=description_string, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/userinfo")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)

async def changereminder(interaction : discord.Interaction, time_reminder : str, userDatabase : UserDatabase):
    if not userDatabase.user_exists(str(interaction.user.id)):
        result_title = f'User Not Found'
        result_description = f'User not found for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/changereminder")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
    else:
        def validate_time(time_str):
            hours, minutes = time_str.split(':')
            if not hours.isdigit() or not minutes.isdigit():
                return False
            hours = int(hours)
            minutes = int(minutes)
            if hours < 0 or hours > 24 or minutes < 0 or minutes > 60:
                return False
            return True
        check = validate_time(time_reminder)
        if check:
            userDatabase.update_time_preference(str(interaction.user.id), time_reminder)
            result_title = f'Preference Time Changed'
            result_description = f'**{interaction.user.mention}** will be notified at {time_reminder}'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="Reminder-Bot says:")
            embed.set_footer(text="/changereminder")
            await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
        else:
            result_title = f'Invalid Output'
            result_description = f'Did not change preference time for **{interaction.user.mention}**'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="Reminder-Bot says:")
            embed.set_footer(text="/changereminder")
            await interaction.response.send_message(file=file, embed=embed, ephemeral=False)

async def deleteuser(interaction : discord.Interaction , userDatabase : UserDatabase):
    username_string = f'token/token_{str(interaction.user.id)}.json'
    if not userDatabase.user_exists(str(interaction.user.id)) and not os.path.exists(username_string):
        result_title = f'User Not Found'
        result_description = f'User not found for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/deleteuser")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
    else:
        os.remove(username_string)
        print(f"The file {username_string} has been deleted successfully.")
        userDatabase.delete_user(str(interaction.user.id))
        result_title = f'**User Deleted**'
        result_description = f'User deleted for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/deleteuser")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)