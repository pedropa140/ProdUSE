import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import random
import datetime

from user import User, UserDatabase


pomodoro_running = True

async def hello(interaction : discord.Interaction):
    options = ["Hi ", "Hey ", "Hello ", "Howdy ", "Hi there ", "Greetings ", "Aloha ", "Bonjour ", "Ciao ", "Hola ", "How's it going? ", "Howdy-do ", "Good day ", "Wassup ", "What's popping? ", "What's up? ", "Hiya ", "What's new? ", "How are you? "]
    current_time = datetime.datetime.now().time().hour
    if current_time > 12:
        options.append("Good Afternoon/ ")
    else:
        options.append("Good Morning/ ")
    chosen_string = options[random.randint(0, len(options) - 1)]
    string = chosen_string + interaction.user.mention
    embed = discord.Embed(title = chosen_string, description=string, color=0xFF5733)
    file = discord.File('images/icon.png', filename='icon.png')
    embed.set_thumbnail(url='attachment://icon.png')
    embed.set_author(name="Reminder-Bot says:")
    embed.set_footer(text="/hello")    
    await interaction.response.send_message(file=file, embed=embed, ephemeral=False)

async def time(interaction : discord.Interaction):
    date = datetime.datetime.now()
    year = str(date.year).zfill(2)
    day = str(date.day).zfill(2)
    month = str(date.month).zfill(2)
    hour = str(date.hour).zfill(2)
    minute = str(date.minute).zfill(2)
    second = str(date.second).zfill(2)

    result_string = f'**Today is:** {year}-{day}-{month}\n**The time is:** {hour}:{minute}:{second}'
    embed = discord.Embed(title=result_string, color=0xFF5733)
    file = discord.File('images/icon.png', filename='icon.png')
    embed.set_thumbnail(url='attachment://icon.png')
    embed.set_author(name="Reminder-Bot says:")
    embed.set_footer(text="/time")
    await interaction.response.send_message(file=file, embed=embed, ephemeral=False)

async def pomodoro(interaction : discord.Interaction, pomodoro_start : str, pomodoro_break : str, intervals : str, userDatabase : UserDatabase):
    if not pomodoro_break.isdigit() or not pomodoro_start.isdigit() or not intervals.isdigit():
        result_title = f'Invalid Output'
        result_description = f'Pomodoro did not start for **{interaction.user.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/pomodoro")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
        return
    
    counter = 0
    study_time = int(pomodoro_start)
    study_seconds = study_time * 60
    break_seconds  = int(pomodoro_break)
    break_seconds = break_seconds * 60
    while counter < intervals:
        result_title = f'Study Time Started'
        result_description = f'Pomodoro started for **{message.author.mention}**\nStart working for {study_time_content} minutes'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/pomodoro")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
        asyncio.sleep(pomodoro_start)

        result_title = f'Break Time Started'
        result_description = f'Pomodoro started for **{message.author.mention}**\nStart chilling for {break_time_content} minutes'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="Reminder-Bot says:")
        embed.set_footer(text="/pomodoro")
        await interaction.response.send_message(file=file, embed=embed, ephemeral=False)
        asyncio.sleep(pomodoro_break)

        counter += 1
        
async def help(interaction : discord.Interaction):
    result_string = f'/Help'
    help_description = f'''How to use {interaction.user.mention}'''
    embed = discord.Embed(title=result_string, description=help_description, color=0xFF5733)
    file = discord.File('images/icon.png', filename='icon.png')
    embed.set_thumbnail(url='attachment://icon.png')
    embed.set_author(name="Reminder-Bot says:")
    embed.add_field(name="/hello", value="returns a friendly greeting/", inline=False)
    embed.add_field(name="/time", value="tells the current time.", inline=False)
    embed.add_field(name="/adduser", value="adds user to the database", inline=False)
    embed.add_field(name="/userinfo", value="returns user information from the database", inline=False)
    embed.add_field(name="/changereminder", value="changes the time that the user wants to be notified of the tasks", inline=False)
    embed.add_field(name="/deleteuser", value="deletes user from the database", inline=False)
    embed.add_field(name="/addtask", value="adds a task to the task list", inline=False)
    embed.add_field(name="/todaytask", value="displays the tasks that end on the current date", inline=False)
    embed.add_field(name="/alltasks", value="shows all uncompleted tasks", inline=False)
    embed.add_field(name="/removetask", value="removes tasks from tasks list", inline=False)
    embed.add_field(name="/pomodoro", value="initializes the pomodoro method", inline=False)
    embed.add_field(name="/help", value="shows the help menu", inline=False)
    embed.set_footer(text="/help")
    await interaction.response.send_message(file=file, embed=embed)