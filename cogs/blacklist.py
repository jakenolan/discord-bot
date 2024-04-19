from discord.ext import commands
import discord
import datetime


class Blacklist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._blacklisted_users = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # Get global blacklist across servers
        for guild in self.bot.guilds:
            data = await self.bot.config.find(guild.id)
            if not data or "blacklist" not in data:
                self._blacklisted_users[guild.id] = []
            else:
                self._blacklisted_users[guild.id] = data["blacklist"]
        # Cog ready
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Add someone to internal blacklist
    @commands.command(name="blacklist", description="Add user to internal blacklist", usage="<user>")
    @commands.has_guild_permissions(ban_members=True)
    async def _blacklist(self, ctx, *, mention=''):
        # Clean up mentioned user id
        mention = mention.replace('<@!', '')
        mention = mention.replace('>', '')
        # If user was not mentioned
        if mention == '':
            await ctx.send(f"{ctx.author.mention} Please give me the user's @")
        # If user in blacklist
        elif mention in self._blacklisted_users[ctx.guild.id]:
            await ctx.send("User already added to internal blacklist")
        # Else add user to blacklist
        else:
            self._blacklisted_users[ctx.guild.id].append(mention)
            await self.bot.config.upsert({"_id": ctx.guild.id, "blacklist": self._blacklisted_users[ctx.guild.id]})
            await ctx.send("User has been added to internal blacklist")
    
    # Remove someone from internal blacklist
    @commands.command(name="unblacklist", description="Remove user from internal blacklist", usage="<user>")
    @commands.has_guild_permissions(ban_members=True)
    async def _unblacklist(self, ctx, *, mention=''):
        # Clean up mentioned user id
        mention = mention.replace('<@!', '')
        mention = mention.replace('>', '')
        # If user was not mentioned
        if mention == '':
            await ctx.send(f"{ctx.author.mention} Please give me the user's @")
        # If user NOT in blacklist
        elif mention not in self._blacklisted_users[ctx.guild.id]:
            await ctx.send("User is not in the internal blacklist")
        # Else remove user from blacklist
        else:
            self._blacklisted_users[ctx.guild.id].remove(mention)
            await self.bot.config.upsert({"_id": ctx.guild.id, "blacklist": self._blacklisted_users[ctx.guild.id]})
            await ctx.send("User has been removed from internal blacklist")

    # Check on join if user is in internal blacklist
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_member_join(self, member):
        try:
            if str(member.id) in self._blacklisted_users[member.guild.id]:
                await member.ban(delete_message_days=7)
                print('Blacklisted user banned upon entry')
        except Exception as e:
            print(e)


def setup(bot):
    bot.add_cog(Blacklist(bot))