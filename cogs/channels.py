import discord
from discord.ext import commands


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._set_channels = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # Get set channels for all servers
        for guild in self.bot.guilds:
            data = await self.bot.config.find(guild.id)
            if not data or "channels" not in data:
                self._set_channels[guild.id] = {}
            else:
                self._set_channels[guild.id] = data["channels"]
        # Cog ready
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Check if there is a set log channel and return
    async def get_log_channel(self, ctx):
        data = await self.bot.config.find(ctx.guild.id)
        # If no data or no channels set tell user
        if not data or "channels" not in data:
            embed = discord.Embed(description=f"There are no channels set")
            await ctx.send(embed=embed)
            return None
        # Else check for logs in channels
        else:
            data = data["channels"]
            # If no logs tell user
            if "logs" not in data:
                embed = discord.Embed(description=f"There is no logs channel set")
                await ctx.send(embed=embed)
                return None
            # Else return logs channel
            else:
                return data["logs"]
    
    # Clean user id for mentions in an embed
    async def clean_mention(self, mention):
        mention = mention.replace('<@!', '<@')
        return mention

    # Boilerplate for logs embed after setting a channel
    async def logsembed(self, ctx, name=''):
        channel = self.bot.get_channel(await self.get_log_channel(ctx))
        if channel:
            embed = discord.Embed(title=f"{name} channel has been set to #{ctx.channel.name}")
            embed.add_field(name='\uFEFF', value=f"Done by {await self.clean_mention(ctx.author.mention)}")
            return channel, embed

    # Dynamic function for setting channel
    async def _set(self, ctx):
        self._set_channels[ctx.guild.id][ctx.command.name] = ctx.channel.id
        await self.bot.config.upsert({"_id": ctx.guild.id, "channels": self._set_channels[ctx.guild.id]})

    # Parent commmand for setting channels
    @commands.group(name='setchannel', aliases=['channel'], description='Set the prupose of this channel', usage='<purpose>')
    @commands.has_guild_permissions(manage_channels=True) # Check to see about other permissions
    async def setchannel(self, ctx):
        if ctx.invoked_subcommand is None:
            # Get list of subcommands
            sublist = []
            for subcommand in ctx.command.walk_commands():
                if subcommand.parents[0] == ctx.command:
                    sublist.append(subcommand.name)

            # Tell user how to use setchannel
            embed = discord.Embed(description="\uFEFF")
            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
            embed.add_field(name="*Set server channels for different automated bot messages*", 
                value="\uFEFF", inline=False)
            embed.add_field(name="To set this channel for automated messages use:", 
                value=f"```{ctx.prefix}setchannel <purpose>```", inline=False)
            embed.add_field(name="Purposes:", 
                value=f"```{sublist}```", inline=False)
            await ctx.channel.send(embed=embed)

    # Subcommand for setting logs channel
    @setchannel.command(name='logs', description='Set this channel for logs')
    async def _logs(self, ctx):
        await self._set(ctx)
        channel, embed = await self.logsembed(ctx, name=ctx.command.name)
        await channel.send(embed=embed)
        await ctx.message.delete()

    # Subcommand for setting welcome channel
    @setchannel.command(name='welcome', description='Set this channel for welcome messages')
    async def _welcome(self, ctx, other=False):
        await self._set(ctx)
        channel, embed = await self.logsembed(ctx, name=ctx.command.name)
        await channel.send(embed=embed)
        await ctx.message.delete()

    # Subcommand for setting goodbye channel
    @setchannel.command(name='goodbye', description='Set this channel for goodbye messages')
    async def _goodbye(self, ctx, other=False):
        await self._set(ctx)
        channel, embed = await self.logsembed(ctx, name=ctx.command.name)
        await channel.send(embed=embed)
        await ctx.message.delete()

    # Subcommand for setting rules channel
    @setchannel.command(name='rules', description='Set this channel for rules')
    async def _rules(self, ctx):
        await self._set(ctx)
        channel, embed = await self.logsembed(ctx, name=ctx.command.name)
        await channel.send(embed=embed)
        await ctx.message.delete()

    # Subcommand for setting roles channel
    @setchannel.command(name='roles', description='Set this channel for roles')
    async def _roles(self, ctx):
        await self._set(ctx)
        channel, embed = await self.logsembed(ctx, name=ctx.command.name)
        await channel.send(embed=embed)
        await ctx.message.delete()

    # Subcommand for setting cafe channel
    @setchannel.command(name='cafe', description='Set this channel to the cafe')
    async def _cafe(self, ctx):
        await self._set(ctx)
        channel, embed = await self.logsembed(ctx, name=ctx.command.name)
        await channel.send(embed=embed)
        await ctx.message.delete()

    # Subcommand for setting verification channel
    @setchannel.command(name='verification', description='Set this channel for verification instructions')
    async def _verification(self, ctx):
        await self._set(ctx)
        channel, embed = await self.logsembed(ctx, name=ctx.command.name)
        await channel.send(embed=embed)
        await ctx.message.delete()

    # Subcommand for setting verification logs channel
    @setchannel.command(name='verificationlogs', description='Set this channel for verification logs')
    async def _verificationlogs(self, ctx):
        await self._set(ctx)
        channel, embed = await self.logsembed(ctx, name=ctx.command.name)
        await channel.send(embed=embed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Setup(bot))