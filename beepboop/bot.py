import os
import asyncio
from datetime import datetime
import logging
import discord
from discord.ext import commands
import aiohttp
import traceback
import sys
import json
from beepboop import __version__

os.chdir(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.WARNING)

EXTENSIONS = [
    'beepboop.cogs.gifs',
    'beepboop.cogs.music',
    'beepboop.cogs.jokes',
    'beepboop.cogs.utils',
    'beepboop.cogs.fun',
    'beepboop.cogs.google',
    # 'beepboop.cogs.crypto',
    # 'beepboop.cogs.lol',
    'beepboop.cogs.spyfall'
]

class BeepBoop(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!!', description='Beep Boop', activity=discord.Game(name='[Alpha %s]' % __version__))
        self.session = aiohttp.ClientSession(loop=self.loop)

        with open('config.json', 'r') as conf:
            self.config = json.load(conf)

        self.token = self.config["token"]

        for extension in EXTENSIONS:
            try:
                self.load_extension(extension)
            except Exception as e:
                print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('Sorry. This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
            traceback.print_tb(error.original.__traceback__)
            print(
                f'{error.original.__class__.__name__}: {error.original}', file=sys.stderr)

    async def on_ready(self):
        print('Logged in as:')
        print('Username: ' + self.user.name)
        print('ID: ' + str(self.user.id))
        print('------')
        self.uptime = datetime.now()
        self.icount = self.command_count = 0


    async def on_message(self, message):
        if message.author.id == self.user.id:
            if hasattr(self, 'icount'):
                self.icount += 1
        elif message.content.startswith('!!'):
            self.command_count += 1

        await self.process_commands(message)

    # async def on_member_join(self, member):
    #     guild = member.guild
    #     fmt = '{} who dis?!'
    #     await guild.send(fmt.format(member.mention))
    
    async def close(self):
        await super().close()
        await self.session.close()

    def run(self):
        super().run(self.token, reconnect=True)


def main():
    bot = BeepBoop()
    bot.run()


if __name__ == '__main__':
    main()
