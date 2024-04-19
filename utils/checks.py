import discord
from discord.ext import commands


# Custom check function to make sure its me
def is_creator():
    def predicate(ctx):
        return ctx.author.id == 123 # Add my creator id here
    return commands.check(predicate)


# Check for yes or no reply
async def yesno(self, ctx, message):
    # Check for a yes or no from author
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel and \
            message.content.lower() in ["yes", "no"]
    # Await for response and act
    message = await self.bot.wait_for("message", check=check)
    if message.content.lower() == "yes":
        return True
    if message.content.lower() == "no":
        return False