import asyncio
from discord.ext import commands
from random import choice
import json
from beepboop import Base
import os


class Jokes(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.music = bot.get_cog("Music")

    @commands.command(pass_context=True, no_pm=True)
    async def joke(self, ctx):
        with open(os.path.join(self.text_directory, 'jokes.json')) as jokes_file:
            jokes = json.loads(jokes_file.read())["jokes"]
            random_line = choice(range(0, len(jokes), 2))
            joke = jokes[random_line]
            await self.bot.say(joke["joke"])
            await asyncio.sleep(3)
            await self.bot.say(joke["punchline"])

            state = self.music.get_voice_state(ctx.message.server)
            print(state)
            summoned_channel = ctx.message.author.voice_channel
            print(summoned_channel)
            if summoned_channel is not None:
                if state.voice is None:
                    success = await ctx.invoke(self.music.summon)
                    if not success:
                        return

                try:
                    player = state.voice.create_ffmpeg_player(os.path.join(self.audio_directory, 'funee_joke.mp3'), after=lambda: self.leave(state, ctx))
                    player.volume = 0.4
                    player.start()
                except Exception as e:
                    fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                    await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

    def leave(self, state, ctx):
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