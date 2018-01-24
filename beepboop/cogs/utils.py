from datetime import datetime
import asyncio
import os
from gtts import gTTS
from discord.ext import commands
import discord
from beepboop.base import Base, Checks


class Utils(Base):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.start_time = datetime.now()
        self.music = bot.get_cog("Music")

    @commands.command(pass_context=True, no_pm=True)
    async def uptime(self, ctx):
        current_datetime = datetime.now()
        diff = current_datetime - self.start_time
        days, seconds = diff.days, diff.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        await self.bot.say(
            "Been up for {} hours, {} minutes and {} seconds".format(
                hours, minutes, seconds)
        )

    @commands.check(Checks.is_owner)
    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def say(self, ctx, *, message: str):
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
                    player = state.voice.create_ffmpeg_player(
                        os.path.join(
                            self.audio_directory, "tts.mp3"
                        ), after=lambda: self.__leave(state, ctx)
                    )
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
            message = self.bot.send_message(
                ctx.message.channel, fmt.format(type(e).__name__, e))
            fut = asyncio.run_coroutine_threadsafe(message, self.bot.loop)
            fut.result()

    @commands.command(pass_context=True, no_pm=True, aliases=['status'])
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
        # game = self.bot.game
        # if not game:
        #     game = 'None'
        channel_count = 0
        for server in self.bot.servers:
            channel_count += len(server.channels)
        if self.embed_perms(ctx.message):
            em = discord.Embed(title='BeepBoop Stats', color=0x32441c)
            em.add_field(name=u'\U0001F553 Uptime', value=time, inline=False)
            em.add_field(name=u'\U0001F4E4 Msgs sent',
                         value=str(self.bot.icount))
            em.add_field(name=u'\U0001F4E5 Cmds received',
                         value=str(self.bot.command_count))
            # em.add_field(name=u'\u2757 Mentions', value=str(self.bot.mention_count))
            em.add_field(name=u'\u2694 Servers',
                         value=str(len(self.bot.servers)))
            em.add_field(name=u'\ud83d\udcd1 Channels',
                         value=str(channel_count))
            # em.add_field(name=u'\u270F Keywords logged', value=str(self.bot.keyword_log))
            # g = u'\U0001F3AE Game'
            # if '=' in game: g = '\ud83c\udfa5 Stream'
            # em.add_field(name=g, value=game)
            mem_usage = '{:.2f} MiB'.format(__import__(
                'psutil').Process().memory_full_info().uss / 1024 ** 2)
            em.add_field(name=u'\U0001F4BE Memory usage:', value=mem_usage)
            # try:
            #     g = git.cmd.Git(working_dir=os.getcwd())
            #     branch = g.execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            #     g.execute(["git", "fetch", "origin", branch])
            #     version = g.execute(["git", "rev-list", "--right-only", "--count", "{}...origin/{}".format(branch, branch)])
            #     if branch == "master":
            #         branch_note = "."
            #     else:
            #         branch_note = " (`" + branch + "` branch)."
            #     if version == '0':
            #         status = 'Up to date%s' % branch_note
            #     else:
            #         latest = g.execute(
            #             ["git", "log", "--pretty=oneline", "--abbrev-commit", "--stat", "--pretty", "-%s" % version,
            #              "origin/%s" % branch])
            #         gist_latest = PythonGists.Gist(description='Latest changes for the selfbot.', content=latest,
            #                                        name='latest.txt')
            #         if version == '1':
            #             status = 'Behind by 1 release%s [Latest update.](%s)' % (branch_note, gist_latest)
            #         else:
            #             status = '%s releases behind%s [Latest updates.](%s)' % (version, branch_note, gist_latest)
            #     em.add_field(name=u'\U0001f4bb Update status:', value=status)
            # except:
            #     pass
            await self.bot.say(embed=em)
        else:
            msg = '**Bot Stats:** ```Uptime: %s\nMessages Sent: %s\nMessages Received: %s\nMentions: %s\nServers: %s```' % (
                time, str(self.bot.icount), str(
                    self.bot.message_count), str(self.bot.mention_count),
                str(len(self.bot.servers)))
            await self.bot.say(msg)
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    async def server(self, ctx):
        server_ctx = ctx.message.server

        online = 0
        for i in server_ctx.members:
            if str(i.status) == 'online' or str(i.status) == 'idle' or str(i.status) == 'dnd':
                online += 1
        all_users = []
        for user in server_ctx.members:
            all_users.append('{}#{}'.format(user.name, user.discriminator))
        all_users.sort()
        all_ = '\n'.join(all_users)

        channel_count = 0
        for channel in server_ctx.channels:
            if channel.type == discord.ChannelType.text:
                channel_count += 1

        role_count = len(server_ctx.roles)
        emoji_count = len(server_ctx.emojis)

        if self.embed_perms(ctx.message):
            em = discord.Embed(color=0xea7938)
            em.add_field(name='Name', value=server_ctx.name)
            em.add_field(name='Owner', value=server_ctx.owner, inline=False)
            em.add_field(name='Members', value=server_ctx.member_count)
            em.add_field(name='Currently Online', value=online)
            em.add_field(name='Text Channels', value=str(channel_count))
            em.add_field(name='Region', value=server_ctx.region)
            em.add_field(name='Verification Level',
                         value=str(server_ctx.verification_level))
            em.add_field(name='Highest role',
                         value=server_ctx.role_hierarchy[0])
            em.add_field(name='Number of roles', value=str(role_count))
            em.add_field(name='Number of emotes', value=str(emoji_count))
            # url = PythonGists.Gist(description='All Users in: %s' % server_ctx.name, content=str(all_), name='server.txt')
            # gist_of_users = '[List of all {} users in this server]({})'.format(server_ctx.member_count, url)
            # em.add_field(name='Users', value=gist_of_users)
            em.add_field(name='Created At', value=server_ctx.created_at.__format__(
                '%A, %d. %B %Y @ %H:%M:%S'))
            em.set_thumbnail(url=server_ctx.icon_url)
            em.set_author(name='Server Info',
                          icon_url='https://i.imgur.com/RHagTDg.png')
            em.set_footer(text='Server ID: %s' % server_ctx.id)
            await self.bot.send_message(ctx.message.channel, embed=em)
        else:
            msg = '**Server Info:** ```Name: %s\nOwner: %s\nMembers: %s\nCurrently Online: %s\nRegion: %s\nVerification Level: %s\nHighest Role: %s\nDefault Channel: %s\nCreated At: %s\nServer avatar: : %s```' % (
                server_ctx.name, server_ctx.owner, server_ctx.member_count, online, server_ctx.region, str(server_ctx.verification_level), server_ctx.role_hierarchy[0], server_ctx.default_channel, server_ctx.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'), server_ctx.icon_url)
            await self.bot.SAY(msg)

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Get response time."""
        msgtime = ctx.message.timestamp.now()
        await (await self.bot.ws.ping())
        now = datetime.now()
        ping = now - msgtime

        if self.embed_perms(ctx.message):
            pong = discord.Embed(title='Pong! Response Time:', description=str(ping.microseconds / 1000.0) + ' ms',
                                 color=0x7A0000)
            pong.set_thumbnail(
                url='http://odysseedupixel.fr/wp-content/gallery/pong/pong.jpg')
            await self.bot.say(embed=pong)
        else:
            await self.bot.say('``Response Time: %s ms``' % str(ping.microseconds / 1000.0))

    @commands.check(Checks.is_owner)
    @commands.command(pass_context=True, hidden=True)
    async def reload(self, ctx, txt: str = None):
        """Reloads all modules."""
        await self.bot.delete_message(ctx.message)
        if txt:
            self.bot.unload_extension(txt)
            try:
                self.bot.load_extension(txt)
            except Exception as e:
                try:
                    txt = 'beepboop.cogs.' + txt
                    self.bot.load_extension(txt)
                except:
                    await self.bot.say('``` {}: {} ```'.format(type(e).__name__, e))
                    return
        else:
            utils = []
            for i in self.bot.extensions:
                utils.append(i)
            fail = False
            l = len(utils)
            for i in utils:
                self.bot.unload_extension(i)
                try:
                    self.bot.load_extension(i)
                except Exception as e:
                    await self.bot.say(
                        'Failed to reload module `{}` ``` {}: {} ```'.format(i, type(e).__name__, e)
                    )
                    fail = True
                    l -= 1
            await self.bot.say('Reloaded {} of {} modules.'.format(l, len(utils)))

    @commands.check(Checks.is_owner)
    @commands.command(pass_context=True)
    async def messagedump(self, ctx, limit, filename, details="yes", reverse="no"):
        """Dump messages."""
        await self.bot.delete_message(ctx.message)
        await self.bot.send_message(ctx.message.channel, "Downloading messages...")
        if not os.path.isdir('message_dump'):
            os.mkdir('message_dump')
        with open("message_dump/" + filename.rsplit('.', 1)[0] + ".txt", "wb+") as f:
            if reverse == "yes":
                if details == "yes":
                    async for message in self.bot.logs_from(ctx.message.channel, int(limit)):
                        content = message.content
                        for attachment in message.attachments:
                            print(attachment)
                            content += ("\n" + attachment['url'])
                        f.write("<{} at {}> {}\n".format(
                            message.author.name, message.timestamp.strftime('%d %b %Y'), content
                        ).encode())

                else:
                    async for message in self.bot.logs_from(ctx.message.channel, int(limit)):
                        content = message.content
                        for attachment in message.attachments:
                            content += ("\n" + attachment['url'])
                        f.write(content.encode() + "\n".encode())
            else:
                if details == "yes":
                    async for message in self.bot.logs_from(ctx.message.channel, int(limit), reverse=True):
                        content = message.content
                        for attachment in message.attachments:
                            content += ("\n" + attachment['url'])
                        f.write("<{} at {}> {}\n".format(
                            message.author.name, message.timestamp.strftime('%d %b %Y'), content).encode())

                else:
                    async for message in self.bot.logs_from(ctx.message.channel, int(limit), reverse=True):
                        content = message.content
                        for attachment in message.attachments:
                            content += ("\n" + attachment['url'])
                        f.write(content.encode() + "\n".encode())
        await self.bot.send_message(ctx.message.channel, "Finished downloading!")


def setup(bot):
    bot.add_cog(Utils(bot))
