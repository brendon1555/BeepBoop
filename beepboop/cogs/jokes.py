import asyncio
from random import choice
import json
import os
from discord import PCMVolumeTransformer, FFmpegPCMAudio
from discord.ext import commands
from beepboop.base import Base

class Jokes(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def joke(self, ctx):
        with open(os.path.join(self.text_directory, 'jokes.json')) as jokes_file:
            jokes = json.loads(jokes_file.read())["jokes"]
            random_line = choice(range(0, len(jokes), 2))
            joke = jokes[random_line]
            await ctx.send(joke["joke"])
            await asyncio.sleep(3)
            await ctx.send(joke["punchline"])

            state = self.bot.get_cog("Music").get_voice_state(ctx.message.guild)
            summoned_channel = ctx.message.author.voice.channel
            if summoned_channel is not None:
                if state.voice is None:
                    success = await ctx.invoke(self.bot.get_cog("Music").summon)
                    if not success:
                        return

                try:
                    source = PCMVolumeTransformer(FFmpegPCMAudio(os.path.join(
                            self.audio_directory, 'funee_joke.mp3'
                        )), volume=0.4)
                    state.voice.play(source, after=lambda: self.leave(state, ctx))
                except Exception as e:
                    fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                    await ctx.send(
                        fmt.format(type(e).__name__, e)
                    )

    def leave(self, state, ctx):
        try:
            state.audio_player.cancel()
            del self.bot.get_cog("Music").voice_states[ctx.message.guild.id]
            disconnect = state.voice.disconnect()
            fut = asyncio.run_coroutine_threadsafe(disconnect, self.bot.loop)
            fut.result()
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            print(fmt.format(type(e).__name__, e))
            message = ctx.send(fmt.format(type(e).__name__, e))
            fut = asyncio.run_coroutine_threadsafe(message, self.bot.loop)
            fut.result()


def setup(bot):
    bot.add_cog(Jokes(bot))
