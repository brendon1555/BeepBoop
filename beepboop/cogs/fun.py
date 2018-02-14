import os
import logging
import asyncio
from discord.ext import commands
from random import choice, randint
from beepboop.base import Base
import discord
from discord import PCMVolumeTransformer, FFmpegPCMAudio

class Fun(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.ball = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it',
                     'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes',
                     'Reply hazy try again',
                     'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                     'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                     'Very doubtful']
        self.regionals = {'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
                          'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}',
                          'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}', 'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}',
                          'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
                          'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
                          'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}',
                          'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}', 'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}',
                          'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
                          'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
                          'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}',
                          'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}', 'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}',
                          'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
                          's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
                          'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}',
                          'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}', 'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}',
                          'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
                          'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}',
                          '0': '0⃣', '1': '1⃣', '2': '2⃣', '3': '3⃣',
                          '4': '4⃣', '5': '5⃣', '6': '6⃣', '7': '7⃣', '8': '8⃣', '9': '9⃣', '!': '\u2757',
                          '?': '\u2753'}
        self.kaomoji = {'tableflip': '(╯°□°）╯︵ ┻━┻', 'tableset': '┬──┬ ノ( ゜-゜ノ)'}

    @commands.command(aliases=['8ball'])
    async def ball8(self, ctx, *, msg: str):
        answer = randint(0, 19)
        if self.embed_perms(ctx.message):
            if answer < 10:
                colour = 0x008000
            elif 10 <= answer < 15:
                colour = 0xFFD700
            else:
                colour = 0xFF0000
            em = discord.Embed(color=colour)
            em.add_field(name='\u2753 Question', value=msg)
            em.add_field(name='\ud83c\udfb1 8ball', value=self.ball[answer], inline=False)
            await ctx.send(embed=em)
        else:
            await ctx.send('\ud83c\udfb1 ``{}``'.format(choice(self.ball)))

    @commands.command(aliases=['choose'])
    async def pick(self, ctx, *, msg: str):
        """Picks randomly from the options provided separated by |"""
        await ctx.send('I choose: {}'.format(choice(msg.split("|"))))

    @commands.command(aliases=["huge"])
    async def big(self, ctx, *, msg):
        """Replace letters with emojis"""
        msg = list(msg)
        regional_list = [self.regionals[x.lower()] if x.isalnum() or x == '!' or x == '?' else x for x in msg]
        regional_output = ' '.join(regional_list)
        await ctx.send(regional_output)

    @commands.command()
    async def flip(self, ctx):
        await ctx.send(self.kaomoji['tableflip'])

    @commands.command()
    async def unflip(self, ctx):
        await ctx.send(self.kaomoji['tableset'])

    @commands.command()
    async def mlg(self, ctx):
        summoned_channel = ctx.message.author.voice.channel
        if summoned_channel is not None:
            vc = ctx.guild.voice_client

            if vc is None:
                await ctx.invoke(self.bot.get_cog("Music").voice_connect)
                if not ctx.guild.voice_client:
                    return
                else:
                    vc = ctx.guild.voice_client
            else:
                if ctx.author not in vc.channel.members:
                    return await ctx.send(f'You must be in **{vc.channel}** to request mlg.', delete_after=30)

            try:
                source = PCMVolumeTransformer(FFmpegPCMAudio(os.path.join(
                        self.audio_directory, 'mlg_airhorn.mp3'
                    )), volume=0.2)
                vc.play(source, after=lambda x: self.leave(ctx))
            except Exception as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                await ctx.send(
                    fmt.format(type(e).__name__, e)
                )

    @commands.command()
    async def yeet(self, ctx):
        summoned_channel = ctx.message.author.voice.channel
        if summoned_channel is not None:
            vc = ctx.guild.voice_client

            if vc is None:
                await ctx.invoke(self.bot.get_cog("Music").voice_connect)
                if not ctx.guild.voice_client:
                    return
                else:
                    vc = ctx.guild.voice_client
            else:
                if ctx.author not in vc.channel.members:
                    await ctx.send(f'You must be in **{vc.channel}** to request yeet.', delete_after=30)

            try:
                source = PCMVolumeTransformer(FFmpegPCMAudio(os.path.join(
                        self.audio_directory, 'yeet.mp3'
                    )), volume=0.2)
                vc.play(source, after=lambda x: self.leave(ctx))
            except Exception as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                await ctx.send(
                    fmt.format(type(e).__name__, e)
                )

    def leave(self, ctx):
        try:
            stop_player = ctx.invoke(self.bot.get_cog("Music").stop_player)
            fut = asyncio.run_coroutine_threadsafe(stop_player, self.bot.loop)
            fut.result()
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            print(fmt.format(type(e).__name__, e))
            message = ctx.send(fmt.format(type(e).__name__, e))
            fut = asyncio.run_coroutine_threadsafe(message, self.bot.loop)
            fut.result()

def setup(bot):
    bot.add_cog(Fun(bot))
