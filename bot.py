import os
import sys
import logging
import discord
from discord.ext import commands
import motor.motor_asyncio

import utils.json_loader
from utils.mongo import Document


# Saving root path
cwd = sys.path[0]
cwd = str(cwd)
print(f"{cwd}\n-----")


# Get prefix
async def get_prefix(bot, message):
    # If in dms because dms cant have a custom prefix
    if not message.guild:
        return commands.when_mentioned_or(default_prefix)(bot, message)
    try:
        data = await bot.config.find(message.guild.id)
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(default_prefix)(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or(default_prefix)(bot, message)


# Setting up the bot object
secret_data = utils.json_loader.read_json("secrets")
default_prefix = secret_data["default_prefix"]
logging.basicConfig(level=logging.INFO)
intents = discord.Intents.all()
bot = commands.Bot(case_insensitive=True, command_prefix=get_prefix, intents=intents)
bot.config_token = secret_data['token']
bot.connection_url = secret_data['mongodb']
bot.version = '0.1'
bot.cwd = cwd


# What happens when the bot is ready to use
@bot.event
async def on_ready():
    # Show the bot is ready and online
    print(f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----")
    print(bot)
    await bot.change_presence(activity=discord.CustomActivity(name=f"Hi, my names {bot.user.name}.\nUse '{bot.command_prefix}' to interact with me!"))

    for document in await bot.config.get_all():
        print(document)
    
    print( 'Initialized database\n-----' )


@bot.event
async def on_message(message):
    # If message is from the bot
    if message.author.bot:
        return
    # Whenever the bot is tagged, respond with its prefix
    if bot.user.mentioned_in(message):
        data = await bot.config.get_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = default_prefix
        else:
            prefix = data["prefix"]
        await message.channel.send(f"My prefix here is `{prefix}`", delete_after=15)
    # Process command and handle insensitive casing
    message.content  = message.content[0].lower() + message.content[1:]
    await bot.process_commands(message)


# Run the bot
if __name__ == '__main__':
    # Setup extra bot variables
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo['jakes']
    bot.config = Document(bot.db, "config")
    bot.invites = Document(bot.db, "invites")
    bot.reaction_roles = Document(bot.db, "reaction_roles")
    bot.cafe = Document(bot.db, "cafe")
    
    # Load all included cogs
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(bot.config_token)