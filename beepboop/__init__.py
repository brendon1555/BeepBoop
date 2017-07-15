import os
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

with open('config.json') as f:
    _config = json.load(f)


class Base(object):

    def __init__(self):
        self.audio_directory = os.path.join(os.path.dirname(__file__), 'audio')
        self.text_directory = os.path.join(os.path.dirname(__file__), 'text')
        self.config = _config

    @staticmethod
    async def cleanup(the_bot, message):
        await the_bot.delete_message(message)

    @staticmethod
    def embed_perms(message):
        return message.author.permissions_in(message.channel).embed_links


class Checks:
    @staticmethod
    def is_owner(ctx):
        print("here")
        print(ctx.message.author.id)
        print(_config['owner_id'])
        print(ctx.message.author.id == _config['owner_id'])
        if ctx.message.author.id == _config['owner_id']:
            return True

        return False
