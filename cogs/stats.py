import discord
from discord.ext import commands


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    async def update_stats_channels(self, guild):
        # Get total members
        total = guild.member_count
        # Split into members and bots
        role = discord.utils.get(guild.roles, name="Bots")
        bots = len(role.members)
        humans = total - bots
        # Get stats data
        data = await self.bot.config.find(guild.id)
        # If data is none or stats disabled
        if not data or "stats" not in data:
            return
        # Else if stats enabled
        else:
            # Get stats channels
            total_channel = self.bot.get_channel(data["stats"]["total"])
            humans_channel = self.bot.get_channel(data["stats"]["humans"])
            bots_channel = self.bot.get_channel(data["stats"]["bots"])
            # Edit locked channels for each stat
            await total_channel.edit(name=f"Total Members: {total}")
            await humans_channel.edit(name=f"Humans: {humans}")
            await bots_channel.edit(name=f"Bots: {bots}")

    # Stats group
    @commands.group(name="stats", invoke_without_command=True)
    async def stats(self, ctx):
        # Create embed for admin help
        embed = discord.Embed(title="Stats Options", description="\uFEFF")
        embed.add_field(name="Enable stats with `{self.bot.prefix}stats enable`", value="\uFEFF", inline=False)
        embed.add_field(name="Disable stats with `{self.bot.prefix}stats disable`", value="\uFEFF", inline=False)
        await ctx.send(embed=embed)

    @stats.command(name='enable')
    async def enablestats(self, ctx):
        # Get stats data
        data = await self.bot.config.find(ctx.guild.id)
        # If data is none or stats disabled
        if not data or "stats" not in data:
            # Create channels
            overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(connect=False)}
            stats_category = await ctx.guild.create_category("Server Stats", overwrites=overwrites)
            total_channel = await ctx.guild.create_voice_channel("total", category=stats_category)
            humans_channel = await ctx.guild.create_voice_channel("humans", category=stats_category)
            bots_channel = await ctx.guild.create_voice_channel("bots", category=stats_category)
            # Create dict
            stats = {}
            stats["category"] = stats_category.id
            stats["total"] = total_channel.id
            stats["humans"] = humans_channel.id
            stats["bots"] = bots_channel.id
            # Save channels to mongodb
            await self.bot.config.upsert({"_id": ctx.guild.id, "stats": stats})
        # Update channels
        await self.update_stats_channels(ctx.guild)

    @stats.command(name='disable')
    async def disablestats(self, ctx):
        # Get stats data
        data = await self.bot.config.find(ctx.guild.id)
        # If data is none or stats disabled
        if not data or "stats" not in data:
            return
        # Else if stats enabled
        else:
            # Get stats channels
            stats_category = discord.utils.get(ctx.guild.categories, id=data["stats"]["category"])
            total_channel = self.bot.get_channel(data["stats"]["total"])
            humans_channel = self.bot.get_channel(data["stats"]["humans"])
            bots_channel = self.bot.get_channel(data["stats"]["bots"])
        # Delete Channels
        await stats_category.delete()
        await total_channel.delete()
        await humans_channel.delete()
        await bots_channel.delete()
        # Delete channels from mongodb
        await self.bot.config.unset({"_id": ctx.guild.id, "stats": 1})

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Reload server stats
        await self.update_stats_channels(member.guild)

    # When someone leaves send a goodbye in goodbye channel
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Reload server stats
        await self.update_stats_channels(member.guild)
    

def setup(bot):
    bot.add_cog(Stats(bot))