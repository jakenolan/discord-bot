import datetime
import discord
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Check if there is a set welcome channel and return
    async def get_welcome_channel(self, member):
        data = await self.bot.config.find(member.guild.id)
        # If no data or no channels
        if not data or "channels" not in data:
            print('There are no channels set')
            return None
        # Else check for welcome
        else:
            data = data["channels"]
            # If no welcome set
            if "welcome" not in data:
                print('There is no welcome channel set')
                return None
            # Else return welcome channel
            else:
                return data["welcome"]

    # Check if there is a set goodbye channel and return
    async def get_goodbye_channel(self, member):
        data = await self.bot.config.find(member.guild.id)
        # If no data or no channels
        if not data or "channels" not in data:
            print('There are no channels set')
            return None
        # Else check for goodbye
        else:
            data = data["channels"]
            # If no goodbye set
            if "goodbye" not in data:
                print('There is no goodbye channel set')
                return None
            # Else return goodbye channel
            else:
                return data["goodbye"]

    async def get_rules_channel(self, ctx):
        data = await self.bot.config.find(ctx.guild.id)
        # If no data or no channels set tell user
        if not data or "channels" not in data:
            print('There are no channels set')
            return None
        # Else check for rules in channels
        else:
            data = data["channels"]
            # If no rules tell user
            if "rules" not in data:
                print('There is no rules channel set')
                return None
            # Else return rules channel
            else:
                return data["rules"]

    # Check if there is a set log channel and return
    async def get_log_channel(self, ctx):
        data = await self.bot.config.find(ctx.guild.id)
        # If no data or no channels set tell user
        if not data or "channels" not in data:
            print('There are no channels set')
            return None
        # Else check for logs in channels
        else:
            data = data["channels"]
            # If no logs tell user
            if "logs" not in data:
                print('There is no logs channel set')
                return None
            # Else return logs channel
            else:
                return data["logs"]

    # Clean user id for mentions in an embed
    async def clean_mention(self, mention):
        mention = mention.replace('<@!', '<@')
        return mention

    # When someone joins send a welcome message in welcome channel
    @commands.Cog.listener()
    async def on_member_join(self, member):
        member = await member.guild.fetch_member(member.id)
        channel = self.bot.get_channel(await self.get_welcome_channel(member))
        rules = self.bot.get_channel(await self.get_rules_channel(member))
        if channel:
            embed = discord.Embed(description=f"***\uFEFF \n Welcome {member.name}!***")
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            embed.add_field(name='\uFEFF', inline=False,
                value=f"To gain full access to the server read the rules in {rules.mention} \n \uFEFF")
            embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
            embed.timestamp = datetime.datetime.utcnow()
            await channel.send(embed=embed)
        channel = self.bot.get_channel(await self.get_log_channel(member))
        if channel:
            embed = discord.Embed(description=F"***\uFEFF \n {await self.clean_mention(member.mention)} joined the server \n \uFEFF***")
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name=F"Account created on:", inline=False,
                value=f"{member.created_at.month}/{member.created_at.day}/{member.created_at.year} \n \uFEFF")
            embed.add_field(name=F"Account created at:", inline=False,
                value=f"{member.created_at.hour} : {member.created_at.minute} \n \uFEFF")
            embed.timestamp = datetime.datetime.utcnow()
            await channel.send(embed=embed)

    # When someone leaves send a goodbye in goodbye channel
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(await self.get_goodbye_channel(member))
        if channel:
            embed = discord.Embed(description='***\uFEFF \n Goodbye from all of us..***')
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Welcome(bot))