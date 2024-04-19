import asyncio
import discord
from discord.ext import commands


class Cafe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.divider = '~   ~   ~   ~   ~'
        self.cafe_name = ''
        self.cafe_open = True
        self.cafe_menu = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    async def get_cafe_channel(self, ctx):
        data = await self.bot.config.find(ctx.guild.id)
        # If no data or no channels set tell user
        if not data or "channels" not in data:
            embed = discord.Embed(description=f"There are no channels set")
            await ctx.send(embed=embed)
            return None
        # Else check for cafe in channels
        else:
            data = data["channels"]
            # If no cafe tell user
            if "cafe" not in data:
                embed = discord.Embed(description=f"There is no cafe channel set")
                await ctx.send(embed=embed)
                return None
            # Else return cafe channel
            else:
                return data["cafe"]

    async def get_cafe_name(self, ctx):
        data = await ctx.bot.cafe.find(ctx.guild.id)
        # If no data is found set name state to an empty string
        if data is None:
            self.cafe_name = ''
        # If name is in data set name state
        elif "cafe_name" in data:
            self.cafe_name = data["cafe_name"]

    async def get_cafe_open(self, ctx):
        data = await ctx.bot.cafe.find(ctx.guild.id)
        # If no data is found return
        if data is None:
            await ctx.bot.cafe.upsert({"_id": ctx.guild.id, "cafe_open": True})
            self.cafe_open = True
            return self.cafe_open
        # If cafe_open is in the data
        elif "cafe_open" in data:
            # Set the cafe_open state
            self.cafe_open = data["cafe_open"]
            # If the cafe is not open send a message
            if self.cafe_open != True:
                await ctx.send('The cafe is currently closed for business. Please come back later!')
            return self.cafe_open
    
    async def get_cafe_menu(self, ctx):
        data = await ctx.bot.cafe.find(ctx.guild.id)
        # If no data is found set menu state to an empty object
        if data is None:
            self.cafe_menu = {}
        # If menu is in data set menu state
        elif "menu" in data:
            self.cafe_menu = data["menu"]
    
    @commands.group(name="cafe")
    async def cafe(self, ctx):
        # Show cafe
        if ctx.invoked_subcommand is None:
            if await self.get_cafe_open(ctx) != True:
                return
            await self.get_cafe_name(ctx)
            embed = discord.Embed(title=self.cafe_name)
            embed.description = f"{self.divider} \n \
                Welcome in! We are open for business. Take a seat anywhere! \
                \n {self.divider} \n \uFEFF"
            embed.set_thumbnail(url=ctx.bot.user.avatar_url)
            cafe_scene = discord.File("config/cafe_scene.jpg", filename="cafe_scene.jpg")
            embed.set_image(url="attachment://cafe_scene.jpg")
            await ctx.send(file=cafe_scene, embed=embed)

    @cafe.command(name='name', aliases=['title'], description='Command description', usage='name')
    @commands.has_guild_permissions(manage_messages=True)
    async def _name(self, ctx, *, name):
        # set cafe_name in state and mongo_db
        self.cafe_name = name
        await self.bot.cafe.upsert({"_id": ctx.guild.id, "cafe_name": name})
        # Send confirmation and clear messages
        bot_message = await ctx.send(f"Cafe name has been changed to {name}!")
        await ctx.message.delete(delay=5)
        await bot_message.delete(delay=5)

    @cafe.command(name='open', description='Command description', usage='open')
    @commands.has_guild_permissions(manage_messages=True)
    async def _open(self, ctx):
        # Set cafe_open bool to true in state and mongodb
        self.cafe_open = True
        await self.bot.cafe.upsert({"_id": ctx.guild.id, "cafe_open": True})
        # Send open confirmation
        await ctx.send('The cafe is now open for business!')

    @cafe.command(name='close', description='Command description', usage='close')
    @commands.has_guild_permissions(manage_messages=True)
    async def _close(self, ctx):
        # Set cafe_open bool to true in state and mongodb
        self.cafe_open = False
        await self.bot.cafe.upsert({"_id": ctx.guild.id, "cafe_open": False})
        # Send closed confirmation
        await ctx.send('The cafe is now closed.')

    @cafe.command(name='add', description='Command description', usage='add')
    @commands.has_guild_permissions(manage_messages=True)
    async def _add(self, ctx, category, item, *, description=""):
        # Make category and item lowercase for reference
        category = category.lower()
        item = item.lower()
        # Add item to state
        if category not in self.cafe_menu:
            self.cafe_menu[category] = {}
        self.cafe_menu[category][item] = description
        # Add new item to mongodb
        await self.bot.cafe.upsert({"_id": ctx.guild.id, "menu": self.cafe_menu})
        # Send confirmation message
        await ctx.send(f"{item} has been added to the menu!")

    @cafe.command(name='remove', aliases=['delete'], description='Command description', usage='remove')
    @commands.has_guild_permissions(manage_messages=True)
    async def _remove(self, ctx, category, *, item):
        # Make category and item lowercase for reference
        category = category.lower()
        item = item.lower()
        # Remove item from mongodb
        await self.get_cafe_menu(ctx)
        del self.cafe_menu[category][item]
        await self.bot.cafe.upsert({"_id": ctx.guild.id, "menu": self.cafe_menu})
        # Send confirmation message
        await ctx.send(f"{item} has been removed from the menu!")

    @commands.command(name='menu', aliases=['showmenu'], description='Show the cafe menu', usage='menu')
    async def _menu(self, ctx):
        # If the cafe is not open
        if await self.get_cafe_open(ctx) != True:
            return
        # Get the menu from mongodb and create embed
        await self.get_cafe_menu(ctx)
        await self.get_cafe_name(ctx)
        embed = discord.Embed(title=f"{self.cafe_name} Menu",
            description=f"{self.divider} \n \
                Here is your menu! \
                \n {self.divider} \n \uFEFF")
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        if self.cafe_menu != {}:
            for category in self.cafe_menu:
                embed.add_field(name=category.capitalize(), value="~ ~ ~ ~ ~", inline=False)
                for item in self.cafe_menu[category]:
                    embed.add_field(name=item, value=f"{self.cafe_menu[category][item]} \n \uFEFF", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='order', aliases=['buy', 'purchase', 'get'],
        description='Order any drink you want off of the cafe menu!', usage='order')
    async def _order(self, ctx, *, item=None):
        # Make sure cafe info is up to date
        await self.get_cafe_name(ctx)
        await self.get_cafe_menu(ctx)
        # If the cafe is not open
        if await self.get_cafe_open(ctx) != True:
            return
        # If no item is given ask if they want to see the menu
        if item is None:
            embed = discord.Embed(title=self.cafe_name)
            embed.description = f"{self.divider} \n \
                **What would you like to order?** \
                \n {self.divider}"
            embed.set_thumbnail(url=ctx.bot.user.avatar_url)
            embed.add_field(name="\uFEFF", value=f"To order use `{ctx.prefix}order <item>`", inline=False)
            embed.add_field(name="\uFEFF", value=f"To see the full menu use `{ctx.prefix}menu`", inline=False)
            await ctx.send(embed=embed)
            return
        # Init variables for parsing and checks
        item = item.lower()
        order = {}
        count = 0
        catCheck = ""
        # If category included in order
        if len(item.split()) > 1:
            (catCheck, rest) = item.lower().split(maxsplit=1)
            for cat in self.cafe_menu:
                if catCheck == cat:
                    order[cat] = self.cafe_menu[cat][rest]
                    category = str(catCheck)
                    item = str(rest)
                    count = 1
                    break
        # Else if category not included in order
        else:
            for cat in self.cafe_menu:
                if item in self.cafe_menu[cat]:
                    order[cat] = self.cafe_menu[cat][item]
                    category = cat
                    count += 1
        # If item is not on the menu
        if count == 0:
            embed = discord.Embed(title=self.cafe_name)
            embed.description = f"{self.divider} \n \
                **Sorry, that is not on the menu!** \
                \n {self.divider}"
            embed.set_thumbnail(url=ctx.bot.user.avatar_url)
            embed.add_field(name="\uFEFF", value=f"To order use `{ctx.prefix}order <item>`", inline=False)
            embed.add_field(name="\uFEFF", value=f"To see the full menu use `{ctx.prefix}menu`", inline=False)
            await ctx.send(embed=embed)
            return
        # If item is in only one category
        if count == 1:
            pass
        # Elif the item is in multiple categories
        elif count > 1:
            # Organize options for embed
            options = " or ".join(order)
            # Create question embed
            question = discord.Embed(title=self.cafe_name)
            question.description = f"{self.divider} \n \
                **Would you like {options}? \n \
                \uFEFF \n \
                Please reply with exact wording!** \
                \n {self.divider}"
            question.set_thumbnail(url=ctx.bot.user.avatar_url)
            question.add_field(name="\uFEFF", value=f"To see the full menu use `{ctx.prefix}menu`", inline=False)
            await ctx.send(embed=question)
            # Wait for user reply
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel
            message = await self.bot.wait_for("message", check=check)
            # If reply not in categories
            if message.content.lower() not in order:
                reply = discord.Embed(title=self.cafe_name)
                reply.description = f"{self.divider} \n \
                    **That was not one of the options. \n \
                    \uFEFF \n \
                    Please try again!** \
                    \n {self.divider}"
                reply.set_thumbnail(url=ctx.bot.user.avatar_url)
                reply.add_field(name="\uFEFF", value=f"To order use `{ctx.prefix}order <item>`", inline=False)
                await ctx.channel.send(embed=reply)
                return
            # Elif reply in categories then update order information
            for possible in order:
                if message.content.lower() == possible:
                    category = str(possible)
        # Create receipt embed
        embed = discord.Embed(title=self.cafe_name)
        embed.description = f"{self.divider} \n \
            Thank you for your order! It will be out soon! \
            \n {self.divider} \n \uFEFF"
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        cafe_order = discord.File("config/cafe_order.jpg", filename="cafe_order.jpg")
        embed.set_image(url="attachment://cafe_order.jpg")
        await ctx.send(file=cafe_order, embed=embed)
        # Delay order and then create deliver embed (toggle delays?)
        await asyncio.sleep(20)
        embed = discord.Embed(title=self.cafe_name)
        embed.description = f"{self.divider} \n \
            Here is your {category} {item} {ctx.author.mention}! \
            \n {self.divider} \n \uFEFF"
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        if category == "hot" or "iced":
            cafe_served = discord.File(f"config/{category}.gif", filename=f"{category}.gif")
            embed.set_image(url=f"attachment://{category}.gif")
        else:
            cafe_served = discord.File("config/misc.gif", filename="misc.gif")
            embed.set_image(url="attachment://misc.gif")
        await ctx.send(file=cafe_served, embed=embed)


def setup(bot):
    bot.add_cog(Cafe(bot))