import os
import json
from functools import wraps
from discord.ext import commands

os.chdir(os.path.dirname(os.path.abspath(__file__)))


_AUDIO_DIRECTORY = os.path.join(os.path.dirname(__file__), 'audio')
_TEXT_DIRECTORY = os.path.join(os.path.dirname(__file__), 'text')

class Base(commands.Cog):

    def __init__(self):
        self.audio_directory = _AUDIO_DIRECTORY
        self.text_directory = _TEXT_DIRECTORY

    @staticmethod
    async def cleanup(the_bot, message):
        await message.delete()

    @staticmethod
    def embed_perms(message):
        return message.author.permissions_in(message.channel).embed_links


class Checks:
    @staticmethod
    def is_owner(ctx):
        if ctx.message.author.id == ctx.bot.config['owner_id']:
            return True

        return False


def typing(func):
    @wraps(func)
    async def wrapped(self, context, *args, **kwargs):
        async with context.typing():
            await func(self, context, *args, **kwargs)
    return wrapped
