import discord
from discord.ext import commands
from discord.ext.commands.core import command


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Check if there is a set log channel and return
    async def get_log_channel(self, guild, channel):
        data = await self.bot.config.find(guild.id)
        # If no data or no channels set tell user
        if not data or "channels" not in data:
            embed = discord.Embed(description=f"There are no channels set")
            await channel.send(embed=embed)
            return None
        # Else check for logs in channels
        else:
            data = data["channels"]
            # If no logs tell user
            if "logs" not in data:
                embed = discord.Embed(description=f"There is no logs channel set")
                await channel.send(embed=embed)
                return None
            # Else return logs channel
            else:
                return data["logs"]

    # Clean user id for mentions in an embed
    async def clean_mention(self, mention):
        mention = mention.replace('<@!', '<@')
        return mention

    # Kick member if you have permissions
    @commands.command(name='kick')
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def _kick(self, ctx, member: discord.Member, *, reason=None):
        await ctx.guild.kick(user=member, reason=reason)
        channel = self.bot.get_channel(await self.get_log_channel(ctx.guild, ctx.channel))
        if channel:
            embed = discord.Embed(title=f"{member.name} kicked", description=reason)
            embed.add_field(name='\uFEFF', value=f"Done by {await self.clean_mention(ctx.author.mention)}")
            await channel.send(embed=embed)
    
    # Ban member if you have permissions
    @commands.command(name='ban')
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def _ban(self, ctx, member: discord.Member, *, reason=None):
        await ctx.guild.ban(user=member, reason=reason)
        channel = self.bot.get_channel(await self.get_log_channel(ctx.guild, ctx.channel))
        if channel:
            embed = discord.Embed(title=f"{member.name} banned", description=reason)
            embed.add_field(name='\uFEFF', value=f"Done by {await self.clean_mention(ctx.author.mention)}")
            await channel.send(embed=embed)

    # Unban member if you have permissions
    @commands.command(name='unban')
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def _unban(self, ctx, member, *, reason=None):
        member = await self.bot.fetch_user(int(member))
        await ctx.guild.unban(member, reason=reason)
        channel = self.bot.get_channel(await self.get_log_channel(ctx.guild, ctx.channel))
        if channel:
            embed = discord.Embed(title=f"{member.name} unbanned", description=reason)
            embed.add_field(name='\uFEFF', value=f"Done by {await self.clean_mention(ctx.author.mention)}")
            await channel.send(embed=embed)

    # Purge messages
    @commands.command(name='purge')
    @commands.guild_only()
    @commands.has_guild_permissions(manage_messages=True)
    async def _purge(self, ctx, amount=10):
        await ctx.channel.purge(limit=amount+1)
        channel = self.bot.get_channel(await self.get_log_channel(ctx.guild, ctx.channel))
        if channel:
            embed = discord.Embed(title=f"#{ctx.channel.name} purged", 
                description=f"{amount} message(s) were cleared")
            mention = await self.clean_mention(ctx.author.mention)
            embed.add_field(name='\uFEFF', value=f"Done by {await self.clean_mention(ctx.author.mention)}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Get log channel and create log embed
        channel = self.bot.get_channel(await self.get_log_channel(message.guild, message.channel))
        if channel:
            embed=discord.Embed(title=f"{message.author.name} deleted a message", description='\uFEFF')
            embed.set_thumbnail(url=message.author.avatar_url)
            embed.add_field(name='Deleted message:', value=message.content, inline=False)
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        # Check for actual edits
        if message_before.content == message_after.content:
            return
        # Get log channel and create log embed
        channel = self.bot.get_channel(await self.get_log_channel(message_before.guild, message_before.guild))
        if channel:
            embed=discord.Embed(title=f"{message_before.author.name} edited a message", description="\uFEFF")
            embed.set_thumbnail(url=message_before.author.avatar_url)
            embed.add_field(name='Before edit:', value=message_before.content, inline=False)
            embed.add_field(name='After edit:', value=message_after.content, inline=False)
            await channel.send(embed=embed)
    

def setup(bot):
    bot.add_cog(Moderation(bot))