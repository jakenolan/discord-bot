import datetime
import discord
from discord.ext import commands


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    async def get_rules_channel(self, ctx):
        data = await self.bot.config.find(ctx.guild.id)
        # If no data or no channels set tell user
        if not data or "channels" not in data:
            embed = discord.Embed(description=f"There are no channels set")
            await ctx.send(embed=embed)
            return None
        # Else check for rules in channels
        else:
            data = data["channels"]
            # If no rules tell user
            if "rules" not in data:
                embed = discord.Embed(description=f"There is no rules channel set")
                await ctx.send(embed=embed)
                return None
            # Else return rules channel
            else:
                return data["rules"]

    async def get_roles_channel(self, ctx):
        data = await self.bot.config.find(ctx.guild.id)
        # If no data or no channels set tell user
        if not data or "channels" not in data:
            embed = discord.Embed(description=f"There are no channels set")
            await ctx.send(embed=embed)
            return None
        # Else check for roles in channels
        else:
            data = data["channels"]
            # If no roles tell user
            if "roles" not in data:
                embed = discord.Embed(description=f"There is no roles channel set")
                await ctx.send(embed=embed)
                return None
            # Else return roles channel
            else:
                return data["roles"]

    # Clean user id for mentions in an embed
    async def clean_mention(self, mention):
        mention = mention.replace('<@!', '<@')
        return mention

    @commands.command(name='agree', description='Agree to the servers rules', usage='agree')
    async def _agree(self, ctx):
        rules = self.bot.get_channel(await self.get_rules_channel(ctx))
        roles = self.bot.get_channel(await self.get_roles_channel(ctx))
        if rules.id == ctx.message.channel.id:
            # Give user the member role for server access
            role = ctx.guild.get_role() # Add memeber role id here
            # Add if role is not assigned to member already
            if role not in ctx.author.roles:
                await ctx.author.add_roles(role, reason="reaction role")
            # Send welcome embed
            embed = discord.Embed(description=f"***\uFEFF \n Welcome {await self.clean_mention(ctx.author.mention)}!***")
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name='\uFEFF', inline=False,
                value=f"Make sure to grab some roles in {roles.mention} \n \uFEFF")
            embed.set_footer(text=ctx.author.guild, icon_url=ctx.author.guild.icon_url)
            embed.timestamp = datetime.datetime.utcnow()
            bot_message = await rules.send(embed=embed)
            # Clean up rules channel
            await ctx.message.delete(delay=10)
            await bot_message.delete(delay=10)
    

def setup(bot):
    bot.add_cog(Rules(bot))