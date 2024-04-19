import os
import discord
from discord.ext import commands
import DiscordUtils


"""
Not in use anymore. 
Discord cracked down on music bots so this was removed from service to respect their new terms of service.
"""


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music = DiscordUtils.Music()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(name='join', description='Joins vc with you')
    async def join(self, ctx):
        await ctx.author.voice.channel.connect()

    @commands.command(name='disconnect', aliases=['disc'], description='Leave your vc')
    async def disconnect(self, ctx):
        await self.clear(ctx)
        await ctx.voice_client.disconnect()

    @commands.command(name='play', description='Play a song in your vc')
    async def play(self, ctx, *, url):
        player = self.music.get_player(guild_id=ctx.guild.id)
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        # If bot not connected to vc
        if voice_client is None:
            await self.join(ctx)
        # If music player not initialized
        if not player:
            player = self.music.create_player(ctx, ffmpeg_error_betterfix=True)
        # Lofi shortcut
        if url.lower() == "lofi":
            url = "" # Custom lofi URL added here
        # Rain shortcut
        if url.lower() == "rain":
            url = "" # Custom rain URL added here
        # If a song is already playing
        if not ctx.voice_client.is_playing():
            await player.queue(url, search=True)
            song = await player.play()
            await ctx.send(f"Playing {song.name}")
        # Else if nothing is playing
        else:
            song = await player.queue(url, search=True)
            await ctx.send(f"Queued {song.name}")

    @commands.command(name='pause', description='Pause music')
    async def pause(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.pause()
        await ctx.send(f"Paused {song.name}")

    @commands.command(name='resume', description='Resume music')
    async def resume(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.resume()
        await ctx.send(f"Resumed {song.name}")

    @commands.command(name='clear', description='Clear current song and queue')
    async def clear(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        await player.stop()
        await ctx.send("Stopped")

    @commands.command(name='loop', aliases=['repear'], description='Toggle repeat for current song')
    async def loop(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.toggle_song_loop()
        if song.is_looping:
            await ctx.send(f"Enabled loop for {song.name}")
        else:
            await ctx.send(f"Disabled loop for {song.name}")

    @commands.command(name='queue', description='Show the queue')
    async def queue(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        await ctx.send(f"{', '.join([song.name for song in player.current_queue()])}")

    @commands.command(name='nowplaying', aliases=['np'], description='What song is now playing')
    async def np(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = player.now_playing()
        await ctx.send(song.name)

    @commands.command(name='skip', description='Skip current song')
    async def skip(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        data = await player.skip(force=True)
        if len(data) == 2:
            await ctx.send(f"Skipped from {data[0].name} to {data[1].name}")
        else:
            await ctx.send(f"Skipped {data[0].name}")

    @commands.command(name='volume', description='Check volume of bot')
    async def volume(self, ctx, vol):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song, volume = await player.change_volume(float(vol) / 100) # volume should be a float between 0 to 1
        await ctx.send(f"Changed volume for {song.name} to {volume*100}%")

    @commands.command(name='remove', description='Remove a song from queue')
    async def remove(self, ctx, index):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.remove_from_queue(int(index))
        await ctx.send(f"Removed {song.name} from queue")
    

def setup(bot):
    bot.add_cog(Music(bot))