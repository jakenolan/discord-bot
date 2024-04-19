import random
import datetime
import discord
from discord.ext import commands


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Global error handling
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Errors to be ignored
        ignore = (commands.CommandNotFound, commands.UserInputError)
        if isinstance(error, ignore):
            return
        # Trip if the command is on cooldown
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f"Please wait {int(s)} seconds to use this command again")
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(f"Please wait {int(m)} minutes and {int(s)} seconds to use this command again")
            else:
                await ctx.send(f"Please wait {int(h)} hours, {int(m)} minutes, and {int(s)} seconds to use this command again")
        # Trip if the command has failed a check
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission to use this command.")
        raise error


def setup(bot):
    bot.add_cog(Errors(bot))