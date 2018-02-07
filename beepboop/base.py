import os
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('config.json') as conf:
    _CONFIG = json.load(conf)

with open('summoners.json') as summoners:
    _SUMMONERS = json.load(summoners)

_AUDIO_DIRECTORY = os.path.join(os.path.dirname(__file__), 'audio')
_TEXT_DIRECTORY = os.path.join(os.path.dirname(__file__), 'text')

class Base(object):

    def __init__(self):
        self.audio_directory = _AUDIO_DIRECTORY
        self.text_directory = _TEXT_DIRECTORY
        self.config = _CONFIG

    @staticmethod
    async def cleanup(the_bot, message):
        await message.delete()

    @staticmethod
    def embed_perms(message):
        return message.author.permissions_in(message.channel).embed_links


class Checks:
    @staticmethod
    def is_owner(ctx):
        print("here")
        print(ctx.message.author.id)
        print(_CONFIG['owner_id'])
        print(ctx.message.author.id == _CONFIG['owner_id'])
        if ctx.message.author.id == _CONFIG['owner_id']:
            return True

        return False
