from os import name
import discord
from discord.ext import commands


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Displays the stats of the bot
    @commands.command(name='botinfo', description='Show the bot stats')
    async def _botinfo(self, ctx):
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))
        
        embed = discord.Embed(description='General information about me!', colour=self.bot.user.colour)
        embed.set_author(name=f"{self.bot.user.name} Stats")
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.add_field(name='\uFEFF', value="\uFEFF", inline=False)
        embed.add_field(name='Total Guilds:', value=serverCount)
        embed.add_field(name='Total Users:', value=memberCount)
        embed.add_field(name='\uFEFF', value="\uFEFF", inline=False)
        embed.add_field(name='Bot Version:', value=self.bot.version)
        embed.add_field(name='Bot Developers:', value="") # Add my @ here
        await ctx.send(embed=embed)

    # Says hi to the user
    @commands.command(name='hi', aliases=['hello', 'hey'], description='Say hello to the bot')
    async def _hi(self, ctx):
        await ctx.send(f"Hi {ctx.author.mention}!")


def setup(bot):
    bot.add_cog(Commands(bot))