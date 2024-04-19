import sys
import json
import discord
from discord.ext import commands

import utils.json_loader


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_prefix = utils.json_loader.read_json("secrets")["default_prefix"]
        self.current_prefixes = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # Get current saved prefixes for all servers
        for guild in self.bot.guilds:
            data = await self.bot.config.find(guild.id)
            if not data or "prefix" not in data:
                self.current_prefixes[guild.id] = self.default_prefix
            else:
                self.current_prefixes[guild.id] = data["prefix"]
        # Cog ready
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    # Change or set prefix for a specific server
    @commands.command(name="prefix", aliases=["changeprefix", "setprefix"],
        description="Change your server's prefix!", usage="<prefix>")
    @commands.has_guild_permissions(administrator=True)
    async def _prefix(self, ctx, prefix=None):
        # If no new prefix is specified
        if prefix is None:
            embed = discord.Embed(description="***\uFEFF \n You did not add a prefix***")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            embed.add_field(name='\uFEFF', inline=False, 
                value=f"To change it use `{self.current_prefixes[ctx.guild.id]}prefix <new prefix>`")
            embed.add_field(name='\uFEFF', inline=False, 
                value=f"For a space after your prefix, use `{self.current_prefixes[ctx.guild.id]}prefix \"<new prefix> \"`")
            embed.add_field(name='\uFEFF', inline=False, 
                value=f"Do you want the prefix to go back to the default `{self.default_prefix}`?")
            embed.add_field(name='\uFEFF', inline=False, value="Reply yes or no")
            bot_message = await ctx.channel.send(embed=embed)
            # Check for proper reply
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and \
                    message.content.lower() in ["yes", "no"]
            # Await for response and act
            message = await self.bot.wait_for("message", check=check)
            if message.content.lower() == "yes":
                self.current_prefixes[ctx.guild.id] = self.default_prefix
                await self.bot.config.upsert({"_id": ctx.guild.id, "prefix": self.default_prefix})
                embed = discord.Embed(description="***\uFEFF \n You want to go back to the default prefix***")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
                embed.add_field(name="\uFEFF", inline=False, 
                    value=f"Setting server's prefix back to default `{self.default_prefix}`")
                bot_reply = await ctx.channel.send(embed=embed)
            if message.content.lower() == "no":
                embed = discord.Embed(description="***\uFEFF \n Please add a new prefix***")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
                embed.add_field(name="\uFEFF", inline=False, 
                    value=f"Use `{self.current_prefixes[ctx.guild.id]}prefix <new prefix>`")
                bot_reply = await ctx.channel.send(embed=embed)
            # Clear all messages
            await ctx.message.delete(delay=5)
            await bot_message.delete(delay=5)
            await message.delete(delay=5)
            await bot_reply.delete(delay=5)
        # Else add new prefix as server prefix
        else:
            self.current_prefixes[ctx.guild.id] = prefix.lower()
            await self.bot.config.upsert({"_id": ctx.guild.id, "prefix": prefix.lower()})
            embed = discord.Embed(description=f"***\uFEFF \n The server's prefix has been set to `{prefix}`***")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            embed.add_field(name="\uFEFF", inline=False,
                    value=f"Use `{prefix}prefix <new prefix>` to change it again!")
            bot_message = await ctx.channel.send(embed=embed)
            # Clear all messages
            await ctx.message.delete(delay=5)
            await bot_message.delete(delay=5)

    # Delete custom prefix
    @commands.command(name="deleteprefix", aliases=["removeprefix"], description="Delete your server's prefix!")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def _deleteprefix(self, ctx):
        await self.bot.config.unset({"_id": ctx.guild.id, "prefix": 1})
        embed = discord.Embed(description="***\uFEFF \n You want to go back to the default prefix***")
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
        embed.add_field(name="\uFEFF", inline=False,
            value=f"Setting server's prefix back to default `{self.default_prefix}`")
        bot_message = await ctx.channel.send(embed=embed)
        # Clear all messages
        await ctx.message.delete(delay=5)
        await bot_message.delete(delay=5)


def setup(bot):
    bot.add_cog(Config(bot))