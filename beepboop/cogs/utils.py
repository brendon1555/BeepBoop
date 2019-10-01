from datetime import datetime
import asyncio
import os
from gtts import gTTS
from discord.ext import commands
import discord
from discord import PCMVolumeTransformer, FFmpegPCMAudio
from beepboop.base import Base, Checks


class Utils(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.start_time = datetime.now()
        self.music = bot.get_cog("Music")

    @commands.command()
    async def uptime(self, ctx):
        current_datetime = datetime.now()
        diff = current_datetime - self.start_time
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        await ctx.send(
            "Been up for {} hours, {} minutes and {} seconds".format(
                hours, minutes, seconds)
        )

    @commands.has_role("Moderator")
    @commands.command(hidden=True)
    async def say(self, ctx, *, message: str):
        """Ignore this"""
        summoned_channel = ctx.message.author.voice.channel
        if summoned_channel is not None:
            tts = gTTS(text=message, lang='en')
            tts.save(os.path.join(self.audio_directory, "tts.mp3"))

            vc = ctx.guild.voice_client
            if vc is None:
                await ctx.invoke(self.bot.get_cog("Music").voice_connect)
                if not ctx.guild.voice_client:
                    return
                else:
                    vc = ctx.guild.voice_client

            try:
                source = PCMVolumeTransformer(FFmpegPCMAudio(os.path.join(
                    self.audio_directory, 'tts.mp3'
            )), volume=1)
                vc.play(source, after=lambda x: self.__leave(ctx))
            except Exception as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                await ctx.send(fmt.format(type(e).__name__, e))

        else:
            await ctx.send("I need you in a Voice Channel to hear me")

    def __leave(self, ctx):
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

    @commands.command(aliases=['status'])
    async def stats(self, ctx):
        """A few stats."""
        uptime = (datetime.now() - self.bot.uptime)
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        if days:
            time = '%s days, %s hours, %s minutes, and %s seconds' % (
                days, hours, minutes, seconds)
        else:
            time = '%s hours, %s minutes, and %s seconds' % (
                hours, minutes, seconds)
        channel_count = 0
        for guild in self.bot.guilds:
            channel_count += len(guild.channels)
        if self.embed_perms(ctx.message):
            em = discord.Embed(title='BeepBoop Stats', color=0x32441c)
            em.add_field(name=u'\U0001F553 Uptime', value=time, inline=False)
            em.add_field(name=u'\U0001F4E4 Msgs sent',
                         value=str(self.bot.icount))
            em.add_field(name=u'\U0001F4E5 Cmds received',
                         value=str(self.bot.command_count))
            em.add_field(name=u'\u2694 Servers',
                         value=str(len(self.bot.guilds)))
            em.add_field(name=u'\ud83d\udcd1 Channels',
                         value=str(channel_count))
            mem_usage = '{:.2f} MiB'.format(__import__(
                'psutil').Process().memory_full_info().uss / 1024 ** 2)
            em.add_field(name=u'\U0001F4BE Memory usage:', value=mem_usage)
            await ctx.send(embed=em)
        else:
            msg = '**Bot Stats:** ```Uptime: %s\nMessages Sent: %s\nMessages Received: %s\nMentions: %s\nServers: %s```' % (
                time, str(self.bot.icount), str(
                    self.bot.message_count), str(self.bot.mention_count),
                str(len(self.bot.guilds)))
            await ctx.send(msg)
        if ctx.guild:
            await ctx.message.delete()

    @commands.command()
    async def server(self, ctx):
        guild_ctx = ctx.message.guild

        online = 0
        for i in guild_ctx.members:
            if str(i.status) == 'online' or str(i.status) == 'idle' or str(i.status) == 'dnd':
                online += 1

        channel_count = 0
        for channel in guild_ctx.channels:
            if isinstance(channel, discord.TextChannel):
                channel_count += 1

        role_count = len(guild_ctx.roles)
        emoji_count = len(guild_ctx.emojis)

        if self.embed_perms(ctx.message):
            em = discord.Embed(color=0xea7938)
            em.add_field(name='Name', value=guild_ctx.name)
            em.add_field(name='Owner', value=guild_ctx.owner, inline=False)
            em.add_field(name='Members', value=guild_ctx.member_count)
            em.add_field(name='Currently Online', value=online)
            em.add_field(name='Text Channels', value=str(channel_count))
            em.add_field(name='Region', value=guild_ctx.region)
            em.add_field(name='Verification Level',
                         value=str(guild_ctx.verification_level))
            em.add_field(name='Highest role',
                         value=guild_ctx.role_hierarchy[0])
            em.add_field(name='Number of roles', value=str(role_count))
            em.add_field(name='Number of emotes', value=str(emoji_count))
            em.add_field(name='Created At', value=guild_ctx.created_at.__format__(
                '%A, %d. %B %Y @ %H:%M:%S'))
            em.set_thumbnail(url=guild_ctx.icon_url)
            em.set_author(name='Server Info',
                          icon_url='https://i.imgur.com/RHagTDg.png')
            em.set_footer(text='Server ID: %s' % guild_ctx.id)
            await ctx.send(embed=em)
        else:
            msg = '**Server Info:** ```Name: %s\nOwner: %s\nMembers: %s\nCurrently Online: %s\nRegion: %s\nVerification Level: %s\nHighest Role: %s\nCreated At: %s\nServer avatar: : %s```' % (
                guild_ctx.name, guild_ctx.owner, guild_ctx.member_count, online, guild_ctx.region, str(guild_ctx.verification_level), guild_ctx.role_hierarchy[0], guild_ctx.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), guild_ctx.icon_url)
            await ctx.send(msg)

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Get response time."""
        msgtime = ctx.message.created_at.now()
        await (await self.bot.ws.ping())
        now = datetime.now()
        ping = now - msgtime

        if self.embed_perms(ctx.message):
            pong = discord.Embed(title='Pong! Response Time:', description=str(ping.microseconds / 1000.0) + ' ms',
                                 color=0x7A0000)
            pong.set_thumbnail(
                url='http://odysseedupixel.fr/wp-content/gallery/pong/pong.jpg')
            await ctx.send(embed=pong)
        else:
            await ctx.send('``Response Time: %s ms``' % str(ping.microseconds / 1000.0))

    @commands.check(Checks.is_owner)
    @commands.command(hidden=True)
    async def reload(self, ctx, txt: str = None):
        """Reloads all modules."""
        if ctx.guild:
            await ctx.message.delete()
        if txt:
            self.bot.unload_extension(txt)
            try:
                self.bot.load_extension(txt)
            except Exception as e:
                try:
                    txt = 'beepboop.cogs.' + txt
                    self.bot.load_extension(txt)
                except:
                    await ctx.send('``` {}: {} ```'.format(type(e).__name__, e))
                    return
        else:
            utils = []
            for i in self.bot.extensions:
                utils.append(i)
            l = len(utils)
            for i in utils:
                self.bot.unload_extension(i)
                try:
                    self.bot.load_extension(i)
                except Exception as e:
                    await ctx.send(
                        'Failed to reload module `{}` ``` {}: {} ```'.format(i, type(e).__name__, e)
                    )
                    l -= 1
            await ctx.send('Reloaded {} of {} modules.'.format(l, len(utils)))

    @commands.check(Checks.is_owner)
    @commands.command(pass_context=True)
    async def messagedump(self, ctx, limit, filename, details="yes", reverse="no"):
        """Dump messages."""
        if ctx.guild:
            await ctx.message.delete()
        await ctx.send("Downloading messages...")
        if not os.path.isdir('message_dump'):
            os.mkdir('message_dump')
        with open("message_dump/" + filename.rsplit('.', 1)[0] + ".txt", "wb+") as f:
            if reverse == "yes":
                if details == "yes":
                    async for message in ctx.message.channel.history(limit=int(limit)):
                        content = message.content
                        for attachment in message.attachments:
                            print(attachment)
                            content += ("\n" + attachment['url'])
                        f.write("<{} at {}> {}\n".format(
                            message.author.name, message.created_at.strftime('%d %b %Y'), content
                        ).encode())

                else:
                    async for message in ctx.message.channel.history(limit=int(limit)):
                        content = message.content
                        for attachment in message.attachments:
                            content += ("\n" + attachment['url'])
                        f.write(content.encode() + "\n".encode())
            else:
                if details == "yes":
                    async for message in ctx.message.channel.history(limit=int(limit), reverse=True):
                        content = message.content
                        for attachment in message.attachments:
                            content += ("\n" + attachment['url'])
                        f.write("<{} at {}> {}\n".format(
                            message.author.name, message.created_at.strftime('%d %b %Y'), content).encode())

                else:
                    async for message in ctx.message.channel.history(limit=int(limit), reverse=True):
                        content = message.content
                        for attachment in message.attachments:
                            content += ("\n" + attachment['url'])
                        f.write(content.encode() + "\n".encode())
        await ctx.send("Finished downloading!")


    @commands.check(Checks.is_owner)
    @commands.command(pass_context=True)
    async def emojis(self, ctx):
        from pprint import pprint
        emoji_list = []
        for emoji in self.bot.emojis:
            emoji_string = "<:{}:{}>".format(emoji.name, emoji.id)
            emoji_list.append(emoji_string)

        pprint(emoji_list)


    @commands.check(Checks.is_owner)
    @commands.command(pass_context=True)
    async def roles(self, ctx):
        for role in ctx.guild.roles:
            print(role.name)
            print(role.id)
            print("------")

def setup(bot):
    bot.add_cog(Utils(bot))
