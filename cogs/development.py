import os
import asyncio
import traceback
import discord
from discord.ext import commands


class Development(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Disconnects the bot when running locally
    @commands.command(name='logout', aliases=['stop', 'close'])
    # @commands.is_owner() is used to make sure only the owner can run this command
    async def _logout(self, ctx):
        await ctx.send(f"Bye {ctx.author.mention}! I am logging out now :wave:")
        await self.bot.logout()

    # Reload all or one of the bots cogs
    @commands.command(name='reload', description='Reload all/one of the bots cogs')
    @commands.has_guild_permissions(administrator=True)
    async def _reload(self, ctx, cog=None):
        # Reload all cogs if no cog is specified
        if not cog:
            async with ctx.typing():
                embed = discord.Embed(title='Reloading all cogs...', description= '\uFEFF', timestamp=ctx.message.created_at)
                for ext in os.listdir("./cogs/"):
                    # For all cogs meant to be running
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(name=f"Reloaded `{ext}`", value='\uFEFF', inline=False)
                        except Exception:
                            try:
                                self.bot.load_extension(f"cogs.{ext[:-3]}")
                                embed.add_field(name=f"Newly loaded `{ext}`", value='\uFEFF', inline=False)
                            except Exception as e:
                                embed.add_field(name=f"Faled to reload `{ext}`", value=e, inline=False)
                        await asyncio.sleep(0.5)
                    # Double check all cogs not meant to be running are unloaded
                    elif ext.endswith(".py") and ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[1:-3]}")
                            embed.add_field(name=f"Unloaded `{ext[1:]}`", value='\uFEFF', inline=False)
                        except Exception:
                            pass
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        # Reload the specific cog given
        else:
            async with ctx.typing():
                embed = discord.Embed(title='Reloading cog...', description= '\uFEFF', timestamp=ctx.message.created_at)
                ext = f"{cog.lower()}.py"
                # Test to see if the cog needs to be unloaded
                if not os.path.exists(f"./cogs/{ext}"):
                    try:
                        if os.path.exists(f"./cogs/_{ext}"):
                            try:
                                self.bot.unload_extension(f"cogs.{ext[:-3]}")
                                embed.add_field(name=f"Unloaded `{ext}`", value='\uFEFF', inline=False)
                            except Exception:
                                pass
                    except Exception:
                        embed.add_field(name=f"Failed to reload `{ext}`", value="This cog does not exist")
                    await asyncio.sleep(0.5)
                # If the cog is still meant to be running
                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(name=f"Reloaded `{ext}`", value='\uFEFF', inline=False)
                    except Exception:
                        try:
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(name=f"Newly loaded `{ext}`", value='\uFEFF', inline=False)
                        except Exception:
                            desired_trace = traceback.format_exc()
                            embed.add_field(name=f"Failed to reload `{ext}`", value=desired_trace, inline=False)
                    await asyncio.sleep(0.5)
                await ctx.send(embed=embed)          


def setup(bot):
    bot.add_cog(Development(bot))