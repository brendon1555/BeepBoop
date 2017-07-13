from discord.ext import commands
from datetime import datetime
from gtts import gTTS
import asyncio
from beepboop import Base
import os


class Utils(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.start_time = datetime.now()
        self.music = bot.get_cog("Music")

    @commands.command(pass_context=True, no_pm=True)
    async def uptime(self, ctx):
        current_datetime = datetime.now()
        diff = current_datetime-self.start_time
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        await self.bot.say("Been up for {} hours, {} minutes and {} seconds".format(hours, minutes, seconds))

    @commands.command(pass_context=True, no_pm=True)
    async def say(self, ctx, *, message):
        """Ignore this"""
        if ctx.message.author.id == '141480928995311616':

            state = self.music.get_voice_state(ctx.message.server)
            summoned_channel = ctx.message.author.voice_channel
            if summoned_channel is not None:
                tts = gTTS(text=message, lang='en')
                tts.save(os.path.join(self.audio_directory, "tts.mp3"))
                if state.voice is None:
                    success = await ctx.invoke(self.music.summon)
                    if not success:
                        return

                try:
                    player = state.voice.create_ffmpeg_player(os.path.join(self.audio_directory, "tts.mp3"), after=lambda: self.__leave(state, ctx))
                    player.volume = 0.4
                    player.start()
                except Exception as e:
                    fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                    await self.bot.say(fmt.format(type(e).__name__, e))

            else:
                await self.bot.say("I need you in a Voice Channel to hear me")

    def __leave(self, state, ctx):
        try:
            state.audio_player.cancel()
            del self.music.voice_states[ctx.message.server.id]
            disconnect = state.voice.disconnect()
            fut = asyncio.run_coroutine_threadsafe(disconnect, self.bot.loop)
            fut.result()
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            print(fmt.format(type(e).__name__, e))
            message = self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
            fut = asyncio.run_coroutine_threadsafe(message, self.bot.loop)
            fut.result()

