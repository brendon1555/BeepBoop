import discord
from discord.ext import commands
from datetime import datetime
import aiohttp

import logging
logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!!'), description='Beep Boop')

extensions = [
    'beepboop.cogs.gifs',
    'beepboop.cogs.jokes',
    'beepboop.cogs.music',
    'beepboop.cogs.utils',
    'beepboop.cogs.fun',
    'beepboop.cogs.google'
]


@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))
    await bot.change_presence(game=discord.Game(name='[Alpha 0.0.3]'))
    bot.uptime = datetime.now()
    bot.game = None
    bot.icount = bot.command_count = 0
    bot.session = aiohttp.ClientSession(loop=bot.loop)

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        formatter = commands.formatter.HelpFormatter()
        await bot.send_message(ctx.message.channel, "{} You are missing required arguments.\n{}".format(ctx.message.author.mention, formatter.format_help_for(ctx, ctx.command)[0]))


@bot.event
async def on_member_join(member):
    server = member.server
    fmt = '{} who dis?!'
    await bot.send_message(server, fmt.format(member.mention))


@bot.event
async def on_message(message):

    if message.author.id == bot.user.id:
        if hasattr(bot, 'icount'):
            bot.icount += 1
    elif message.content.startswith('!!'):
        bot.command_count += 1

    await bot.process_commands(message)

if __name__ == "__main__":
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.run('MTkwNDI0OTM0ODc3NjI2MzY4.DEJOyw.h33o0TCgJFZjpIV7b_Tg5FxLYdA')
