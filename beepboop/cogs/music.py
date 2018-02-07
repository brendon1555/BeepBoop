import os
import asyncio
import discord
from discord.ext import commands
from beepboop.base import Base, _AUDIO_DIRECTORY
import youtube_dl


# if not discord.opus.is_loaded():
#     # the 'opus' library here is opus.dll on windows
#     # or libopus.so on linux in the current directory
#     # you should replace this with the location the
#     # opus library is located in and with the proper filename.
#     # note that on windows this DLL is automatically provided for you
#     discord.opus.load_opus('opus')

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(_AUDIO_DIRECTORY, '%(extractor)s-%(id)s-%(title)s.%(ext)s'),
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')

    @classmethod
    async def from_url(cls, url, *, loop=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, ytdl.extract_info, url)
        
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)


class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    # def is_playing(self):
    #     if self.voice is None or self.current is None:
    #         return False

    #     # player = self.current.player
    #     # return not self.voice.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.voice.is_playing():
            self.voice.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.current.channel.send('Now playing ' + str(self.current))
            self.voice.play(self.current.player, after=lambda e: print('Player error: %s' % e) if e else None)
            await self.play_next_song.wait()


class Music(Base):
    """Voice related commands.
    Works in multiple servers at once.
    """
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, guild):
        state = self.voice_states.get(guild.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[guild.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await channel.connect()
        state = self.get_voice_state(channel.guild)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.InvalidArgument:
            await ctx.send('This is not a voice channel...')
        except discord.ClientException:
            await ctx.send('Already in a voice channel...')
        else:
            await ctx.send('Ready to play audio in ' + channel.name)

    @commands.command()
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice.channel
        if summoned_channel is None:
            await ctx.send('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.guild)
        if state.voice is None:
            state.voice = await summoned_channel.connect()
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command()
    async def moveto(self, ctx, *, channel: discord.VoiceChannel):
        """Move to a channel"""
        state = self.get_voice_state(ctx.message.guild)
        if state.voice is not None:
            await state.voice.move_to(channel)
        else:
            await ctx.send("I am not connected to any voice channel on this server!")

        return True

    @commands.command()
    async def leave(self, ctx):
        for client in self.bot.voice_clients:
            if client.guild == ctx.message.guild:
                return await client.disconnect()

        return await ctx.send("I am not connected to any voice channel on this server!")

    @commands.command()
    async def play(self, ctx, *, song: str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.guild)

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await YTDLSource.from_url(
                song, 
                loop=self.bot.loop
            )
            player.volume = 0.02
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await ctx.send(fmt.format(type(e).__name__, e))
        else:
            entry = VoiceEntry(ctx.message, player)
            await ctx.send('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command()
    async def volume(self, ctx, value: int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.guild)
        if state.voice.is_playing():
            state.current.player.volume = value / 100
            await ctx.send('Set the volume to {:.0%}'.format(state.current.player.volume))

    @commands.command()
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.guild)
        if state.voice.is_playing():
            state.voice.pause()

    @commands.command()
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.guild)
        if state.voice.is_playing():
            state.voice.resume()

    @commands.command()
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        guild = ctx.message.guild
        state = self.get_voice_state(guild)

        if state.voice.is_playing():
            state.voice.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[guild.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command()
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.guild)
        if not state.voice.is_playing():
            await ctx.send('Not playing any music right now...')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await ctx.send('Requester requested skipping song...')
            state.voice.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await ctx.send('Skip vote passed, skipping song...')
                state.voice.skip()
            else:
                await ctx.send('Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await ctx.send('You have already voted to skip this song.')

    @commands.command()
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.guild)
        if state.current is None:
            await ctx.send('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await ctx.send('Now playing {} [skips: {}/3]'.format(state.current, skip_count))
    #
    # @commands.command()
    # async def song(self, ctx):
    #     """Plays a song.
    #     If there is a song currently in the queue, then it is
    #     queued until the next song is done playing.
    #     This command automatically searches as well from YouTube.
    #     The list of supported sites can be found here:
    #     https://rg3.github.io/youtube-dl/supportedsites.html
    #     """
    #     state = self.get_voice_state(ctx.message.server)
    #
    #     if state.voice is None:
    #         success = await ctx.invoke(self.summon)
    #         if not success:
    #             return
    #
    #     try:
    #         player = state.voice.create_ffmpeg_player('funee_joke.mp3')
    #         player.start()
    #     except Exception as e:
    #         fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
    #         await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
    #     else:
    #         player.volume = 0.6
    #         entry = VoiceEntry(ctx.message, player)
    #         await ctx.send('Enqueued ' + str(entry))
    #         await state.songs.put(entry)


def setup(bot):
    bot.add_cog(Music(bot))
