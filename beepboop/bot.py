from datetime import datetime
import logging
import discord
from discord.ext import commands
import aiohttp
from beepboop import __version__
from beepboop.base import _CONFIG

logging.basicConfig(level=logging.DEBUG)

BOT = commands.Bot(command_prefix=commands.when_mentioned_or('!!'), description='Beep Boop')

EXTENSIONS = [
    'beepboop.cogs.gifs',
    'beepboop.cogs.jokes',
    'beepboop.cogs.music',
    'beepboop.cogs.utils',
    'beepboop.cogs.fun',
    'beepboop.cogs.google'
]


@BOT.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(BOT.user))
    await BOT.change_presence(game=discord.Game(name='[Alpha %s]' % __version__))
    BOT.uptime = datetime.now()
    BOT.game = None
    BOT.icount = BOT.command_count = 0
    BOT.session = aiohttp.ClientSession(loop=BOT.loop)

# @BOT.event
# async def on_command_error(error, ctx):
#     if isinstance(error, commands.errors.MissingRequiredArgument):
#         formatter = commands.formatter.HelpFormatter()
#         await BOT.send_message(
#             ctx.message.channel, 
#             "{} You are missing required arguments.\n{}".format(
#                 ctx.message.author.mention, 
#                 formatter.format_help_for
#                 (ctx, ctx.command)[0]
#             )
#         )


@BOT.event
async def on_member_join(member):
    server = member.server
    fmt = '{} who dis?!'
    await BOT.send_message(server, fmt.format(member.mention))


@BOT.event
async def on_message(message):

    if message.author.id == BOT.user.id:
        if hasattr(BOT, 'icount'):
            BOT.icount += 1
    elif message.content.startswith('!!'):
        BOT.command_count += 1

    await BOT.process_commands(message)

def main():
    for extension in EXTENSIONS:
        try:
            BOT.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    BOT.run(_CONFIG['api_key'])

if __name__ == "__main__":
    main()