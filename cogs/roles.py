import typing
import emojis
import discord
from discord.ext import commands
from discord import emoji


class RoleErrors(commands.CommandError):
    # Reaction roles are not setup properly for this guild
    async def no_data(self):
        pass


def is_setup():
    async def wrap_func(ctx):
        data = await ctx.bot.reaction_roles.find(ctx.guild.id)
        # Init check for data
        if data is None:
            return True
            # await RoleErrors().no_data(ctx)
        return True
    return commands.check(wrap_func)


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_reaction_roles = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    async def get_current_reactions(self, guild_id):
        data = await self.bot.reaction_roles.find(guild_id)
        # Init check for data
        if data is None:
            await RoleErrors().no_data()
        # Update state and clean guild_id
        else:
            self.guild_reaction_roles = data
            del data["_id"]
            return data 

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

    async def rebuild_roles_embed(self, ctx):
        # Fetch set roles channel and objects
        channel_id = await self.get_roles_channel(ctx)
        channel = await self.bot.fetch_channel(channel_id)
        guild = await self.bot.fetch_guild(ctx.guild.id)
        # Rework reaction roles embeds
        reaction_roles = await self.get_current_reactions(ctx.guild.id)
        # Each category key is the name of the category
        for category in reaction_roles:
            message = await channel.fetch_message(reaction_roles[category]["message_id"])
            await message.clear_reactions()
            embed = discord.Embed(title=category)
            desc = ""
            # If there are roles in the category
            if "roles" in reaction_roles[category]:
                for item in reaction_roles[category]["roles"]:
                    role = guild.get_role(reaction_roles[category]["roles"][item][0])
                    givendesc = reaction_roles[category]["roles"][item][1]
                    desc += f"{item}: {givendesc}\n"
                    await message.add_reaction(item)
            embed.description = desc
            await message.edit(embed=embed)
    
    @commands.group(name="roles", aliases=["rr"], invoke_without_command=True)
    @commands.guild_only()
    async def roles(self, ctx):
        await ctx.send('Placeholder text') # Update with setup help

    @roles.command(name="addcategory")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @is_setup()
    async def _add_category(self, ctx, *, category=None):
        # Get roles channel
        channel = self.bot.get_channel(await self.get_roles_channel(ctx))
        if channel:
            # If no category name was given
            if category is None:
                embed = discord.Embed(description="\uFEFF")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
                embed.add_field(name="*You did not add a category name*", 
                    value="\uFEFF", inline=False)
                embed.add_field(name=f"Add a category with `{ctx.prefix}{ctx.invoked_with} <name>`?", 
                    value=f"\uFEFF", inline=False)
                await channel.send(embed=embed)
            # Name was given
            else:
                # Add new embed in the roles channel
                embed = discord.Embed(title=category)
                message = await channel.send(embed=embed)
                # Add category to mongodb
                self.guild_reaction_roles[category] = {"message_id": int(message.id)}
                await self.bot.reaction_roles.upsert({
                    "_id": ctx.guild.id, 
                    category: self.guild_reaction_roles[category]
                })
                await ctx.send("Category is now added")

    @roles.command(name="removecategory", aliases=["deletecategory"])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @is_setup()
    async def _remove_category(self, ctx, *, category=None):
        # Get roles channel
        channel = self.bot.get_channel(await self.get_roles_channel(ctx))
        if channel:
            # If no category name was given
            if category is None:
                embed = discord.Embed(description="\uFEFF")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
                embed.add_field(name="*You did not add a category name*", 
                    value="\uFEFF", inline=False)
                embed.add_field(name=f"Add a category with `{ctx.prefix}{ctx.invoked_with} <name>`?", 
                    value=f"\uFEFF", inline=False)
                await channel.send(embed=embed)
            # Name was given
            else:
                # Remove category from discord, mongodb, and state
                reaction_roles = await self.get_current_reactions(ctx.guild.id)
                message = await channel.fetch_message(reaction_roles[category]["message_id"])
                await message.delete()
                await self.bot.reaction_roles.unset({"_id": ctx.guild.id, category: reaction_roles[category]})
                del self.guild_reaction_roles[category]
                await ctx.send("Category is now deleted")

    @roles.command(name="addrole")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @is_setup()
    async def _add_role(self, ctx, category, emoji: typing.Union[discord.Emoji, str], role: discord.Role, *, description):
        # Check data before adding reaction role
        data = await self.get_current_reactions(ctx.guild.id)
        # If category does not exist
        if category not in data:
            await ctx.send("You need to add a category to add the reaction role too. This is placeholder text")
            return
        # If no roles in category yet
        if "roles" not in data[category]:
            self.guild_reaction_roles[category]["roles"] = {}
        # Else check to make sure maximum reacts not hit
        elif "roles" in data[category]:
            reacts = data[category]["roles"]
            # If reacts has hit max of 20 for category
            if len(reacts) >= 20:
                embed = discord.Embed(description="\uFEFF")
                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_author(name=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)
                embed.add_field(name="*Category has hit its maximum number of roles*", 
                    value="\uFEFF", inline=False)
                await ctx.channel.send(embed=embed)
                return
        # Grab message_id for category
        message_id = data[category]["message_id"]
        # If not a discord emoji
        if not isinstance(emoji, discord.Emoji):
            emoji = emojis.get(emoji)
            emoji = emoji.pop()
        # If a discord emoji but not usable
        elif isinstance(emoji, discord.Emoji):
            if not emoji.is_usable():
                await ctx.send("I cant use that emoji. This is placeholder text")
                return
        # Set emoji, update state, update mongodb, and rebuild embed
        emoji = str(emoji)
        self.guild_reaction_roles[category]["roles"][emoji] = [role.id, description]
        await self.bot.reaction_roles.upsert({
            "_id": ctx.guild.id,
            category: self.guild_reaction_roles[category]
        }) # Need to iterate through categories in reaction roles
        await self.rebuild_roles_embed(ctx)
        await ctx.send("Role is now added. This is placeholder text")

    @roles.command(name="removerole")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles=True)
    @is_setup()
    async def _remove_role(self, ctx, category, emoji: typing.Union[discord.Emoji, str]):
        # Grab data
        data = await self.get_current_reactions(ctx.guild.id)
        # Grab message_id for category
        message_id = data[category]["message_id"]
        # If not a discord emoji
        if not isinstance(emoji, discord.Emoji):
            emoji = emojis.get(emoji)
            emoji = emoji.pop()
        # Set emoji, update state, update mongodb, and rebuild embed
        emoji = str(emoji)
        del self.guild_reaction_roles[category]["roles"][emoji]
        await self.bot.reaction_roles.upsert({
            "_id": ctx.guild.id, 
            category: self.guild_reaction_roles[category]
        })
        await self.rebuild_roles_embed(ctx)
        await ctx.send("Role is now removed. This is placeholder text")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # If there is no data for guild
        data = await self.bot.config.find(payload.guild_id)
        if not payload.guild_id or not data: # or not data.get("is_enabled"):
            return
        # If reaction role is not in mongodb
        self.guild_reaction_roles = await self.get_current_reactions(payload.guild_id)
        # If reaction roles arent None
        if self.guild_reaction_roles != None:
            category = ""
            for cat in self.guild_reaction_roles:
                if self.guild_reaction_roles[cat]["message_id"] == payload.message_id:
                    category = cat
            if category == "" or str(payload.emoji) not in self.guild_reaction_roles[category]["roles"]:
                return
            # Get role and member objects
            guild = await self.bot.fetch_guild(payload.guild_id)
            role = guild.get_role(self.guild_reaction_roles[category]["roles"][str(payload.emoji)][0])
            member = await guild.fetch_member(payload.user_id)
            # Add if role is not assigned to member already
            if role not in member.roles:
                await member.add_roles(role, reason="reaction role")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # If there is no data for the guild
        data = await self.bot.config.find(payload.guild_id)
        if not payload.guild_id or not data: # or not data.get("is_enabled"):
            return
        # If reaction role is not in guild
        self.guild_reaction_roles = await self.get_current_reactions(payload.guild_id)
        # If reaction roles arent None
        if self.guild_reaction_roles != None:
            category = ""
            for cat in self.guild_reaction_roles:
                if self.guild_reaction_roles[cat]["message_id"] == payload.message_id:
                    category = cat
            if category == "" or str(payload.emoji) not in self.guild_reaction_roles[category]["roles"]:
                return
            # Get role and member objects
            guild = await self.bot.fetch_guild(payload.guild_id)
            role = guild.get_role(self.guild_reaction_roles[category]["roles"][str(payload.emoji)][0])
            member = await guild.fetch_member(payload.user_id)
            # Remove if role is in member's roles
            if role in member.roles:
                await member.remove_roles(role, reason="reaction role")


def setup(bot):
    bot.add_cog(Roles(bot))