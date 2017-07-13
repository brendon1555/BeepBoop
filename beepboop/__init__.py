import os


class Base(object):

    def __init__(self):
        self.audio_directory = os.path.join(os.path.dirname(__file__), 'audio')
        self.text_directory = os.path.join(os.path.dirname(__file__), 'text')

    @staticmethod
    async def cleanup(the_bot, message):
        await the_bot.delete_message(message)
