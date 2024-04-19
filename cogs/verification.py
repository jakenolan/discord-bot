import datetime
import asyncio
import discord
import emojis
from discord.ext import commands


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verify_instructions = ""
        self.tickets = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    # Clean user id for mentions in an embed
    async def clean_mention(self, mention):
        mention = mention.replace('<@!', '<@')
        return mention

    async def get_verification_channel(self, guild, channel):
        data = await self.bot.config.find(guild)
        # If no data or no channels set tell user
        if not data or "channels" not in data:
            embed = discord.Embed(description=f"There are no channels set")
            await channel.send(embed=embed)
            return None
        # Else check for verification in channels
        else:
            data = data["channels"]
            # If no verification tell user
            if "verification" not in data:
                embed = discord.Embed(description=f"There is no verification channel set")
                await channel.send(embed=embed)
                return None
            # Else return verification channel
            else:
                return data["verification"]

    async def get_verificationlogs_channel(self, guild, channel):
        data = await self.bot.config.find(guild)
        # If no data or no channels set tell user
        if not data or "channels" not in data:
            embed = discord.Embed(description=f"There are no channels set")
            await channel.send(embed=embed)
            return None
        # Else check for verification logs in channels
        else:
            data = data["channels"]
            # If no verification logs tell user
            if "verificationlogs" not in data:
                embed = discord.Embed(description=f"There is no verification logs channel set")
                await channel.send(embed=embed)
                return None
            # Else return verification logs channel
            else:
                return data["verificationlogs"]
    
    async def ticket_opened(self, ticket, member):
        # Get verification instructions
        verification_channel = self.bot.get_channel(await self.get_verification_channel(ticket.guild.id, ticket.id))
        history = await verification_channel.history().flatten()
        self.verify_instructions = history[0].embeds[0].fields[0].value
        # Send message to @ user
        await ticket.send(f"Hi {member.mention}!")
        # Remind user how to verify
        async with ticket.typing():
            await asyncio.sleep(3)
            await ticket.send('\uFEFF')
            await ticket.send('Let me post the instructions here for you: \n \uFEFF')
            await asyncio.sleep(3)
            embed = discord.Embed(title="How to Verify", description='~ ~ ~ ~ ~')
            embed.add_field(name="\uFEFF", value=self.verify_instructions, inline=False)
            embed.add_field(name="\uFEFF", value='~ ~ ~ ~ ~', inline=False)
            embed.add_field(name="\uFEFF", value='*Reactions below are for admin use*', inline=False)
            check = await ticket.send(embed=embed)
        # Add reactions to embed message for admin check
        emoji = emojis.encode(':white_check_mark:')
        emoji = emojis.get(emoji)
        emoji = emoji.pop()
        await check.add_reaction(emoji)
        emoji = emojis.encode(':x:')
        emoji = emojis.get(emoji)
        emoji = emoji.pop()
        await check.add_reaction(emoji)
        # Explain how approval will work
        async with ticket.typing():
            await asyncio.sleep(3)
            await ticket.send('\uFEFF')
            await ticket.send('For faster verification follow the instructions above accurately!')
            await ticket.send('Post the images here and an admin will approve of them later.')
            await ticket.send('I will automatically give you the verified role once an admin approves.')
            await ticket.send('\uFEFF')
        

    # Verification group
    @commands.group(name="verification", invoke_without_command=True)
    async def verification(self, ctx):
        # Create embed for admin help
        embed = discord.Embed(title="Verification System", description="\uFEFF")
        embed.add_field(name="Placeholder for help text", value="\uFEFF", inline=False)
        await ctx.send(embed=embed)

    # Instructions for users on how to verify
    @verification.command(name="instructions:")
    async def verificationinstructions(self, ctx, *, instructions):
        # Get verification channel
        channel = self.bot.get_channel(await self.get_verification_channel(ctx.guild.id, ctx.channel.id))
        if channel:
            # Save instructions to state
            self.verify_instructions = instructions
            # Clear out all messages in verification channel
            await channel.purge()
            # Create instructions embed
            embed = discord.Embed(title="How to Verify", description="\uFEFF")
            embed.add_field(name="\uFEFF", value=instructions, inline=False)
            bot_message = await channel.send(embed=embed)
            # Add reaction to embed message
            emoji = emojis.encode(':clipboard:')
            emoji = emojis.get(emoji)
            emoji = emoji.pop()
            await bot_message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # If there is no data for guild
        data = await self.bot.config.find(payload.guild_id)
        if not payload.guild_id or not data: # or not data.get("is_enabled"):
            return
        # Get guild, channel, instructions, and member objects
        guild = self.bot.get_guild(payload.guild_id)
        channel = self.bot.get_channel(await self.get_verification_channel(guild.id, payload.channel_id))
        history = await channel.history().flatten()
        instructions = history[0]
        member = await guild.fetch_member(payload.user_id)
        # Check if verification channel and not bot reacting
        if channel.id == payload.channel_id and payload.user_id != self.bot.user.id:
            # If user does not already have a ticket open
            if member.id not in self.tickets:
                # Open new ticket channel for user with proper permissions
                overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    member: discord.PermissionOverwrite(view_channel=True)}
                ticket = await guild.create_text_channel(f"{member.name}-ticket", overwrites=overwrites)
                # Add ticket name and id to state
                self.tickets[member.id] = ticket.id
                # Run automatic messages method
                await self.ticket_opened(ticket, member)
        # Check if ticket channel, admin permissions, and not bot
        if payload.channel_id in self.tickets.values() \
            and member.guild_permissions.administrator and payload.user_id != self.bot.user.id:
            # Get verified user
            for item in self.tickets:
                if self.tickets[item] == payload.channel_id:
                    # Get ticket channel
                    ticket = self.bot.get_channel(self.tickets[item])
                    # Try to get the user from server
                    try:
                        verified_user = await guild.fetch_member(item)
                    # If error (user not in server)
                    except Exception as e:
                        # Send error message embed
                        embed = discord.Embed(title="Verification Error", description='~ ~ ~ ~ ~')
                        embed.add_field(name="\uFEFF", value=e, inline=False)
                        embed.add_field(name="\uFEFF", value='~ ~ ~ ~ ~', inline=False)
                        embed.add_field(name="\uFEFF", value='*User most likely left the server*', inline=False)
                        embed.add_field(name="\uFEFF", value='*Deleting ticket shortly*', inline=False)
                        await ticket.send(embed=embed)
                        # Delete ticket after 10 seconds
                        await asyncio.sleep(10)
                        if payload.user_id in self.tickets:
                            await ticket.delete()
                            del self.tickets[payload.user_id]
                        # Remove verification reaction
                        for reaction in instructions.reactions:
                            async for user in reaction.users():
                                if user.id != self.bot.user.id:
                                    await reaction.remove(user)
            # If ticket was approved
            if emojis.decode(payload.emoji.name) == ':white_check_mark:':
                # Give user verified role
                role = discord.utils.get(guild.roles,name="Verified") # This needs to be changed by server
                if role not in verified_user.roles:
                    await verified_user.add_roles(role, reason="reaction role")
                # Add verification log
                channel = self.bot.get_channel(await self.get_verificationlogs_channel(guild.id, payload.channel_id))
                if channel:
                    embed = discord.Embed(description=F"***{await self.clean_mention(verified_user.mention)} Verified \n \uFEFF***")
                    embed.add_field(name=f"Verified by {await self.clean_mention(member.name)}", value="\uFEFF", inline=False)
                    embed.set_thumbnail(url=verified_user.avatar_url)
                    embed.timestamp = datetime.datetime.utcnow()
                    await channel.send(embed=embed)
                # Delete ticket channel
                if verified_user.id in self.tickets:
                    ticket = self.bot.get_channel(self.tickets[verified_user.id])
                    await ticket.delete()
                    del self.tickets[verified_user.id]
                # Remove verification reaction
                for reaction in instructions.reactions:
                    async for user in reaction.users():
                        if user.id != self.bot.user.id:
                            await reaction.remove(user)
            # If ticket was denied
            if emojis.decode(payload.emoji.name) == ':x:':
                # Delete ticket channel
                if payload.user_id in self.tickets:
                    ticket = self.bot.get_channel(self.tickets[payload.user_id])
                    await ticket.delete()
                    del self.tickets[payload.user_id]
                # Remove verification reaction
                for reaction in instructions.reactions:
                    async for user in reaction.users():
                        if user.id != self.bot.user.id:
                            await reaction.remove(user)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # If there is no data for guild
        data = await self.bot.config.find(payload.guild_id)
        if not payload.guild_id or not data: # or not data.get("is_enabled"):
            return
        # Check if verification channel and not bot reacting
        channel = self.bot.get_channel(await self.get_verification_channel(payload.guild_id, payload.channel_id))
        if channel.id == payload.channel_id and payload.user_id != self.bot.user.id:
            # When reaction removed delete channel and state
            if payload.user_id in self.tickets:
                ticket = self.bot.get_channel(self.tickets[payload.user_id])
                await ticket.delete()
                del self.tickets[payload.user_id]
    

def setup(bot):
    bot.add_cog(Verification(bot))